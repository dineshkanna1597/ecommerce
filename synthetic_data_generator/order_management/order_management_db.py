from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

class DatabaseConnection:
    """
    This class handles the database connection and provides methods 
    for committing or rolling back transactions before closing the connection.
    """

    def __init__(self):
        """
        Initializes the database connection using credentials stored in environment variables.
        """
        self.conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),  # Database host (e.g., localhost or an IP address)
            user=os.getenv('MYSQL_USER'),  # Database username
            password=os.getenv('MYSQL_PASSWORD'),  # Database password
            database=os.getenv('ORDER_MANAGEMENT_DB')  # Target database name
        )
        self.cursor = self.conn.cursor()  # Create a cursor object for executing SQL queries

    def commit_and_close(self):
        """
        Commits the transaction and closes the database connection.
        This should be used when operations are successfully completed.
        """
        self.conn.commit()  # Commit any pending database changes
        self.cursor.close()  # Close the cursor
        self.conn.close()  # Close the database connection

    def rollback_and_close(self):
        """
        Rolls back the transaction and closes the database connection.
        This should be used when an error occurs and changes should not be saved.
        """
        self.conn.rollback()  # Rollback any uncommitted changes
        self.cursor.close()  # Close the cursor
        self.conn.close()  # Close the database connection

class OrderManagement(DatabaseConnection):
    def customer_order_tb(self):
        try:
            query = '''
            CREATE TABLE customer_order(
            order_id VARCHAR(255) PRIMARY KEY, 
            customer_id INT NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES user_management.customer_bio(id)
            )
        '''
            self.cursor.execute(query)
            return 'customer order table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def order_products_tb(self):
        try:
            query = '''
            CREATE TABLE order_products(
            id INT AUTO_INCREMENT PRIMARY KEY, 
            order_id VARCHAR(255) NOT NULL,
            product_price_id INT NOT NULL,
            quantity INT NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(order_id,product_price_id),
            FOREIGN KEY (order_id) REFERENCES customer_order(order_id),
            FOREIGN KEY (product_price_id) REFERENCES inventory_management.product_price(id)
            )
        '''
            self.cursor.execute(query)
            return 'order products table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def order_status_tb(self):
        try:
            query = '''
            CREATE TABLE order_status(
            id INT AUTO_INCREMENT PRIMARY KEY, 
            order_id VARCHAR(255) NOT NULL,
            updated_at DATETIME NOT NULL,
            order_status VARCHAR(100) NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(order_id,updated_at),
            FOREIGN KEY (order_id) REFERENCES customer_order(order_id)
            )
        '''
            self.cursor.execute(query)
            return 'order status table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def order_summary_tb(self):
        try:
            query = '''
            CREATE TABLE order_summary( 
            order_id VARCHAR(255) PRIMARY KEY, 
            items_subtotal DECIMAL(10,2) NOT NULL,
            tax DECIMAL(10,2) NOT NULL,
            discount DECIMAL(10,2) NOT NULL,
            grand_total DECIMAL(10,2) NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            FOREIGN KEY (order_id) REFERENCES customer_order(order_id)
            )
        '''
            self.cursor.execute(query)
            return 'order summary table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
obj = OrderManagement()

print(obj.order_status_tb())