from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import coalesce,from_json, col, explode, expr, sum, desc, row_number, regexp_replace, current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, ArrayType, IntegerType

# Initialize Spark session with tuned configurations.
spark = SparkSession.builder \
    .appName("pySparkStreaming") \
    .config("spark.sql.shuffle.partitions", "100") \
    .config("spark.sql.streaming.stateStore.maintenanceInterval", "60s") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.autoBroadcastJoinThreshold", 10 * 1024 * 1024) \
    .getOrCreate()

spark.conf.set("spark.cassandra.connection.host", "HOST")
spark.conf.set("spark.cassandra.auth.username", "USERNAME")
spark.conf.set("spark.cassandra.auth.password", "USERPASSWORD")

# Define schemas
customer_schema = StructType([
    StructField("orderId", StringType(), True),
    StructField("customerId", StringType(), True),
    StructField("name", StringType(), True),
    StructField("mobileNumber", StringType(), True),
    StructField("emailId", StringType(), True),
    StructField("address", StringType(), True),
    StructField("eventTime", TimestampType(), True)
])

inventory_schema = StructType([
    StructField("orderId", StringType(), True),
    StructField("itemsOrdered", ArrayType(
        StructType([
            StructField("product", StringType(), True),
            StructField("material", StringType(), True),
            StructField("soldBy", StringType(), True),
            StructField("quantity", IntegerType(), True),
            StructField("totalPrice", StringType(), True)
        ])
    ), True),
    StructField("eventTime", TimestampType(), True)
])

order_schema = StructType([
    StructField("orderId", StringType(), True),
    StructField("orderStatus", StringType(), True),
    StructField("orderSummary", StructType([
        StructField("itemsSubtotal", StringType(), True),
        StructField("tax", StringType(), True),
        StructField("discount", StringType(), True),
        StructField("grandTotal", StringType(), True)
    ])),
    StructField("created_at", TimestampType(), True),
    StructField("eventTime", TimestampType(), True)
])

payment_schema = StructType([
    StructField("orderId", StringType(), True),
    StructField("transactionId", StringType(), True),
    StructField("paymentType", StringType(), True),
    StructField("paymentMethod", StringType(), True),
    StructField("amount", StringType(), True),
    StructField("paymentStatus", StringType(), True),
    StructField("processedAt", TimestampType(), True),
    StructField("eventTime", TimestampType(), True)
])

shipment_schema = StructType([
    StructField("orderId", StringType(), True),
    StructField("trackerId", StringType(), True),
    StructField("deliveryTo", StructType([
        StructField("name", StringType(), True),
        StructField("mobileNumber", StringType(), True),
        StructField("address", StringType(), True)
    ])),
    StructField("shippingStatus", StringType(), True),
    StructField("updated_at", TimestampType(), True),
    StructField("eventTime", TimestampType(), True)
])

# Read from Kafka
kafka_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "HOST:PORT") \
    .option("subscribe", "customer_created,inventory_created,payment_created,order_created,shipment_created") \
    .option("startingOffsets", "earliest") \
    .option("maxOffsetsPerTrigger", 100) \
    .load()

# Cast Kafka data to strings
parsed_df = kafka_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# Parse and flatten each topic
customer_df = parsed_df.filter("key = 'customer'") \
    .select(from_json(col("value"), customer_schema).alias("customer")) \
    .select(
        col("customer.orderId"),
        col("customer.address").alias("country"),
        col("customer.eventTime").alias("customer_eventTime")
    )

inventory_df = parsed_df.filter("key = 'inventory'") \
    .select(from_json(col("value"), inventory_schema).alias("inventory")) \
    .select(
        col("inventory.orderId"),
        explode(col("inventory.itemsOrdered")).alias("item"),
        col("inventory.eventTime").alias("inventory_eventTime")
    ) \
    .select(
        col("orderId"),
        col("item.product"),
        col("item.material"),
        col("item.soldBy"),
        col("item.quantity"),
        regexp_replace(
            regexp_replace(col("item.totalPrice"), "[^0-9.]", ""), ",", ""
        ).cast("double").alias("amount"),
        col("inventory_eventTime")
    )

order_df = parsed_df.filter("key = 'order'") \
    .select(from_json(col("value"), order_schema).alias("order")) \
    .filter(col("order.orderStatus") == "Confirmed") \
    .select(
        col("order.orderId"),
        col("order.orderStatus"),
        col("order.orderSummary"),
        col("order.created_at"),
        col("order.eventTime").alias("order_eventTime")
    ) \
    .withWatermark("order_eventTime", "30 minutes")

payment_df = parsed_df.filter("key = 'payment'") \
    .select(from_json(col("value"), payment_schema).alias("payment")) \
    .filter(col("payment.paymentStatus") == "paid") \
    .select(
        col("payment.orderId"),
        col("payment.transactionId"),
        col("payment.amount"),
        col("payment.eventTime").alias("payment_eventTime")
    )

shipment_df = parsed_df.filter("key = 'shipment'") \
    .select(from_json(col("value"), shipment_schema).alias("shipment")) \
    .filter(col("shipment.shippingStatus") == "Delivered") \
    .select(
        col("shipment.orderId"),
        col("shipment.trackerId"),
        col("shipment.deliveryTo"),
        col("shipment.updated_at"),
        col("shipment.eventTime").alias("shipment_eventTime")
    )

# Join all streams
joined_df = order_df.alias("o") \
    .join(
        payment_df.alias("p"), 
        expr("o.orderId = p.orderId AND o.order_eventTime BETWEEN p.payment_eventTime - interval 15 minutes AND p.payment_eventTime + interval 15 minutes")
    ) \
    .join(
        shipment_df.alias("s"),
        expr("o.orderId = s.orderId AND o.order_eventTime BETWEEN s.shipment_eventTime - interval 15 minutes AND s.shipment_eventTime + interval 15 minutes")
    ) \
    .join(
        inventory_df.alias("i"),
        expr("o.orderId = i.orderId")
    ) \
    .join(
        customer_df.alias("c"),
        expr("o.orderId = c.orderId AND o.order_eventTime BETWEEN c.customer_eventTime - interval 15 minutes AND c.customer_eventTime + interval 15 minutes")
    )
# Process each micro-batch of data
def process_batch(batch_df, epoch_id):
    if not batch_df.rdd.isEmpty():
        batch_timestamp = current_timestamp()

        # Aggregate current batch
        batch_agg_df = batch_df.groupBy("c.country", "i.product", "i.material") \
            .agg(
                sum("i.quantity").alias("batch_quantity"),
                sum("i.amount").alias("batch_amount")
            )

        # Load existing quantity data
        existing_quantity_df = spark.read \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="YOURTABLENAME", keyspace="YOURKEYSPACE") \
            .load()

        # Load existing amount data
        existing_amount_df = spark.read \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="YOURTABLENAME", keyspace="YOURKEYSPACE") \
            .load()

        # Merge cumulative quantity
        cumulative_qty = batch_agg_df.alias("new").join(
            existing_quantity_df.alias("old"),
            on=[
                col("new.country") == col("old.country"),
                col("new.product") == col("old.product"),
                col("new.material") == col("old.material")
            ],
            how="outer"
        ).select(
            coalesce(col("new.country"), col("old.country")).alias("country"),
            coalesce(col("new.product"), col("old.product")).alias("product"),
            coalesce(col("new.material"), col("old.material")).alias("material"),
            (coalesce(col("new.batch_quantity"), lit(0)) + coalesce(col("old.total_quantity"), lit(0))).alias("total_quantity")
        )

        # Merge cumulative amount
        cumulative_amt = batch_agg_df.alias("new").join(
            existing_amount_df.alias("old"),
            on=[
                col("new.country") == col("old.country"),
                col("new.product") == col("old.product"),
                col("new.material") == col("old.material")
            ],
            how="outer"
        ).select(
            coalesce(col("new.country"), col("old.country")).alias("country"),
            coalesce(col("new.product"), col("old.product")).alias("product"),
            coalesce(col("new.material"), col("old.material")).alias("material"),
            (coalesce(col("new.batch_amount"), lit(0.0)) + coalesce(col("old.total_amount"), lit(0.0))).alias("total_amount")
        )

        # Ranking by quantity
        rank_window_qty = Window.partitionBy("country").orderBy(desc("total_quantity"))
        ranked_qty = cumulative_qty.withColumn("rank", row_number().over(rank_window_qty)) \
                                   .withColumn("timestamp", batch_timestamp)

        # Ranking by amount
        rank_window_amt = Window.partitionBy("country").orderBy(desc("total_amount"))
        ranked_amt = cumulative_amt.withColumn("rank", row_number().over(rank_window_amt)) \
                                   .withColumn("timestamp", batch_timestamp)

        # Write top N by quantity
        ranked_qty.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .options(table="YOURTABLENAME", keyspace="YOURKEYSPACE") \
            .option("confirm.truncate", "true") \
            .save()

        # Write top N by amount
        ranked_amt.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .options(table="YOURTABLENAME", keyspace="YOURKEYSPACE") \
            .option("confirm.truncate", "true") \
            .save()


# Apply foreachBatch to streaming query
query = joined_df.writeStream \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", "hdfs://hadoop-master:9000/user/data/checkpoint_dir") \
    .trigger(processingTime="30 seconds") \
    .start()

query.awaitTermination()
