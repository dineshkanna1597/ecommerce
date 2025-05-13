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
            database=os.getenv('SHIPPING_MANAGEMENT_DB')  # Target database name
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

class ShippingManagement(DatabaseConnection):
    def shipment_order_tb(self):
        try:
            query = '''
            CREATE TABLE shipment_order(
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id VARCHAR(255) NOT NULL,
            delivery_to VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(order_id),
            FOREIGN KEY (order_id) REFERENCES order_management.customer_order(order_id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'shipment order table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
    def shipment_tracker_tb(self):
        try:
            query = '''
            CREATE TABLE shipment_tracker(
            tracker_id VARCHAR(255) PRIMARY KEY,
            shipment_id INT NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            FOREIGN KEY (shipment_id) REFERENCES shipment_order(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'shipment tracker table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
    def shipment_status_tb(self):
        try:
            query = '''
            CREATE TABLE shipment_status(
            id INT AUTO_INCREMENT PRIMARY KEY,
            tracker_id VARCHAR(255) NOT NULL,
            updated_at DATETIME NOT NULL,
            shipment_status VARCHAR(20) NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(tracker_id,last_updated_at),
            FOREIGN KEY (tracker_id) REFERENCES shipment_tracker(tracker_id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'shipment status created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
obj = ShippingManagement()

print(obj.shipment_status_tb())