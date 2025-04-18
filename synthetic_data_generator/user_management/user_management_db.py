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
            database=os.getenv('USER_MANAGEMENT_DB')  # Target database name
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

class UserManagement(DatabaseConnection):
    def customer_bio_tb(self):
        try:
            query = '''
            CREATE TABLE customer_bio(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            mobile_number VARCHAR(50) UNIQUE NOT NULL,
            email_id VARCHAR(50) UNIQUE NOT NULL,
            dob DATE NOT NULL,
            gender VARCHAR(15) NOT NULL,
            last_updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        '''
            self.cursor.execute(query)
            return 'customer bio table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
    def country_tb(self):
        try:
            query = '''
            CREATE TABLE country(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(15) UNIQUE NOT NULL,
            last_updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )        
        '''
            self.cursor.execute(query)
            return 'country table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

    def state_tb(self):
        try:
            query = '''
            CREATE TABLE state(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            country_id INT NOT NULL,
            last_updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE(name,country_id),
            FOREIGN KEY (country_id) REFERENCES country(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'state table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

    def city_tb(self):
        try:
            query = '''
            CREATE TABLE city(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            state_id INT NOT NULL,
            last_updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE(name,state_id),
            FOREIGN KEY (state_id) REFERENCES state(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'city table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    def postalcode_tb(self):
        try:
            query = '''
            CREATE TABLE postalcode(
            id INT AUTO_INCREMENT PRIMARY KEY,
            postalcode VARCHAR(30) NOT NULL,
            city_id INT NOT NULL,
            last_updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE(postalcode,city_id),
            FOREIGN KEY (city_id) REFERENCES city(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'postalcode table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def street_tb(self):
        try:
            query = '''
            CREATE TABLE street(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            postalcode_id INT NOT NULL,
            last_updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE(name,postalcode_id),
            FOREIGN KEY (postalcode_id) REFERENCES postalcode(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'street table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def address_tb(self):
        try:
            query = '''
            CREATE TABLE address(
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            street_id INT NOT NULL,
            last_updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE(customer_id,street_id),
            FOREIGN KEY (customer_id) REFERENCES customer_bio(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (street_id) REFERENCES street(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'address table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
table_obj = UserManagement()
print(table_obj.postalcode_tb())