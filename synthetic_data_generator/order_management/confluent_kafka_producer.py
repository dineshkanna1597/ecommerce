from confluent_kafka import Producer
import json
from datetime import datetime, timezone
from order_details import OrderDetails  # Import OrderDetails from order_details.py

# Configuration for Kafka producer
conf = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'order-producer'
}

# Initialize the Kafka producer
producer = Producer(conf)

# Callback for delivery report
def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"✅ Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}]")

# Helper function to get current UTC time in ISO 8601 format
def current_event_time():
    return datetime.now(timezone.utc).isoformat()

# Function to publish order messages to Kafka
def publish_order_messages():
    obj = OrderDetails()
    order_data = obj.confirm_order()

    # Create output messages with event time
    customer_output = {
        "orderId": order_data["orderId"],
        "customerId": order_data["customerDetails"]["id"],
        "name": order_data["customerDetails"]["name"],
        "mobileNumber": order_data["customerDetails"]["mobileNumber"],
        "emailId": order_data["customerDetails"]["emailId"],
        "address": order_data["customerDetails"]["address"]["country"],
        "eventTime": current_event_time()
    }

    inventory_output = {
        "orderId": order_data["orderId"],
        "itemsOrdered": order_data["orderDetails"]["itemsOrdered"],
        "eventTime": current_event_time()
    }

    order_output = {
        "orderId": order_data["orderId"],
        "orderStatus": order_data["orderDetails"]["orderStatus"],
        "orderSummary": order_data["orderDetails"]["orderSummary"],
        "created_at": order_data["orderDetails"]["created_at"],
        "eventTime": current_event_time()
    }

    payment_output = {
        "orderId": order_data["orderId"],
        "transactionId": order_data["paymentDetails"]["transactionId"],
        "paymentType": order_data["paymentDetails"]["paymentType"],
        "paymentMethod": order_data["paymentDetails"]["paymentMethod"],
        "amount": order_data["paymentDetails"]["amount"],
        "paymentStatus": order_data["paymentDetails"]["paymentStatus"],
        "processedAt": order_data["paymentDetails"]["processedAt"],
        "eventTime": current_event_time()
    }

    shipment_output = {
        "orderId": order_data["orderId"],
        "trackerId": order_data["shippingDetails"]["trackerId"] if order_data["shippingDetails"] else None,
        "deliveryTo": order_data["shippingDetails"]["deliveryTo"] if order_data["shippingDetails"] else None,
        "shippingStatus": order_data["shippingDetails"]["shippingStatus"] if order_data["shippingDetails"] else None,
        "updated_at": order_data["shippingDetails"]["updated_at"] if order_data["shippingDetails"] else None,
        "eventTime": current_event_time()
    }

    # Produce messages to Kafka
    producer.produce("customer_created", key="customer", value=json.dumps(customer_output), callback=delivery_report)
    producer.produce("inventory_created", key="inventory", value=json.dumps(inventory_output), callback=delivery_report)
    producer.produce("order_created", key="order", value=json.dumps(order_output), callback=delivery_report)
    producer.produce("payment_created", key="payment", value=json.dumps(payment_output), callback=delivery_report)
    producer.produce("shipment_created", key="shipment", value=json.dumps(shipment_output), callback=delivery_report)

    # Flush to ensure delivery
    producer.flush()

if __name__ == "__main__":
    publish_order_messages()
