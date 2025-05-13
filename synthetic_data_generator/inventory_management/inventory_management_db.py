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
            database=os.getenv('INVENTORY_MANAGEMENT_DB')  # Target database name
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

class InventoryManagement(DatabaseConnection):
    
    def product_tb(self):
        try:
            query = '''
            CREATE TABLE products(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(30) UNIQUE NOT NULL, 
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL
            )
        '''
            self.cursor.execute(query)
            return 'product table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

    def material_tb(self):
        try:
            query = '''
            CREATE TABLE materials(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(30) UNIQUE NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL
            )
        '''
            self.cursor.execute(query)
            return 'material table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
    def category_tb(self):
        try:    
            query = '''
            CREATE TABLE categories(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(30) UNIQUE NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL
            )
        '''
            self.cursor.execute(query)
            return 'category table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def seller_tb(self):
        try:
            query = '''
            CREATE TABLE sellers(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(30) UNIQUE NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL
            )
        '''
            self.cursor.execute(query)
            return 'seller table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def product_category_tb(self):
        try:     
            query = '''
            CREATE TABLE product_category(
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            category_id INT NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        '''
            self.cursor.execute(query)
            return 'product category table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
    def product_price_tb(self):
        try:
            query = '''
            CREATE TABLE product_price(
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            material_id INT NOT NULL,
            seller_id INT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(product_id,material_id,seller_id),
            FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materials(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (seller_id) REFERENCES sellers(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''' 
            self.cursor.execute(query)
            return 'product price table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

    def product_tax_tb(self):
        try:
            query = '''
            CREATE TABLE product_tax(
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            material_id INT NOT NULL,
            seller_id INT NOT NULL,
            tax DECIMAL(10,2) NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(product_id,material_id,seller_id),
            FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materials(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (seller_id) REFERENCES sellers(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''' 
            self.cursor.execute(query)
            return 'product tax table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
    def product_discount_tb(self):
        try:
            query = '''
            CREATE TABLE product_discount(
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            material_id INT NOT NULL,
            seller_id INT NOT NULL,
            discount DECIMAL(10,2) NOT NULL,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(product_id,material_id,seller_id),
            FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materials(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (seller_id) REFERENCES sellers(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''' 
            self.cursor.execute(query)
            return 'product discount table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
    def product_quantity_tb(self):
        try:
            query = '''
            CREATE TABLE product_quantity(
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            material_id INT NOT NULL,
            seller_id INT NOT NULL,
            quantity INT NOT NULL DEFAULT 100,
            created_at DATETIME NOT NULL,
            last_updated_at DATETIME NOT NULL,
            UNIQUE(product_id,material_id,seller_id),
            FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materials(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (seller_id) REFERENCES sellers(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''' 
            self.cursor.execute(query)
            return 'product quantity table created successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

table_obj = InventoryManagement()

print(table_obj)