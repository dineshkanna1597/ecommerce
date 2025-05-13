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
            database=os.getenv('TRANSACTION_MANAGEMENT_DB')  # Target database name
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

class TransactionManagement(DatabaseConnection):
    def payment_type_tb(self):
        try:
            query = '''
            CREATE TABLE payment_type(
            id INT AUTO_INCREMENT PRIMARY KEY, 
            payment_types VARCHAR(20) UNIQUE NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL
            )
        '''
            self.cursor.execute(query)
            return 'payment type table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def payment_method_tb(self):
        try:
            query = '''
            CREATE TABLE payment_method(
            id INT AUTO_INCREMENT PRIMARY KEY, 
            payment_methods VARCHAR(15) UNIQUE NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL
            )
        '''
            self.cursor.execute(query)
            return 'payment method table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def payment_status_tb(self):
        try:
            query = '''
            CREATE TABLE payment_status(
            id INT AUTO_INCREMENT PRIMARY KEY, 
            payment_status VARCHAR(10) UNIQUE NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL
            )
        '''
            self.cursor.execute(query)
            return 'payment status table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def payment_transaction_tb(self):
        try:
            query = '''
            CREATE TABLE payment_transaction(
            id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id VARCHAR(255) NULL,
            order_id VARCHAR(255) NOT NULL, 
            payment_type_id INT NOT NULL, 
            payment_method_id INT NULL,
            amount DECIMAL(10,2) NOT NULL,
            payment_status_id INT NOT NULL, 
            created_at DATETIME NOT NULL,
            processed_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(transaction_id,order_id),
            FOREIGN KEY (order_id) REFERENCES order_management.customer_order(order_id),
            FOREIGN KEY (payment_type_id) REFERENCES payment_type(id),
            FOREIGN KEY (payment_method_id) REFERENCES payment_method(id),
            FOREIGN KEY (payment_status_id) REFERENCES payment_status(id)
            )
        '''
            self.cursor.execute(query)
            return 'payment transaction table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
obj = TransactionManagement()

print(obj.payment_transaction_tb())