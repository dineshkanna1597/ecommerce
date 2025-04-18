from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from decimal import Decimal
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()


# Load the API key from environment variables
API_KEY = os.getenv('API_KEY')

# Define the name of the API key header to be used in requests
API_KEY_NAME = "X-API-Key"

# Initialize an APIRouter instance to register routes
router = APIRouter()

class DatabaseConnection:
    """
    A class to handle database connection and provide commit/rollback functionality.
    """

    def __init__(self):
        """
        Initializes the database connection using credentials stored in environment 
        variables.
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

class InventoryDetails(BaseModel):
    product_name: str
    material_name: str
    category_name: str
    seller_name: str
    price: Decimal
    tax_rate: Decimal
    discount_rate: Decimal

class Product(DatabaseConnection):
    """
    Class for handling product insertions and operations related to products.
    """

    def insert(self,product_name):
        """
        Inserts a new product into the database.
        """
        try:
            sql = 'INSERT IGNORE INTO products(name) VALUES (%s)'
            self.cursor.execute(sql,[product_name])
            self.commit_and_close()
            return 'product inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class Material(DatabaseConnection):
    """
    Class for handling material insertions and operations related to materials.
    """

    def insert(self,material_name):
        """
        Inserts a new material into the database.
        """
        try:
            sql = 'INSERT IGNORE INTO materials(name) VALUES (%s)'
            self.cursor.execute(sql,[material_name])
            self.commit_and_close()
            return 'material inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class Category(DatabaseConnection):
    """
    A class to manage category insertions into the database.
    """

    def insert(self,category_name):
        """
        Inserts a new category into the database.
        """
        try:
            sql = 'INSERT IGNORE INTO categories(name) VALUES (%s)'
            self.cursor.execute(sql,[category_name])
            self.commit_and_close()
            return 'category inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class Seller(DatabaseConnection):
    """
    A class to manage seller insertions into the database.
    """

    def insert(self,seller_name):
        """
        Inserts a new seller into the database.
        """
        try:
            sql = 'INSERT IGNORE INTO sellers(name) VALUES (%s)'
            self.cursor.execute(sql,[seller_name])
            self.commit_and_close()
            return 'seller inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ProductCategory(DatabaseConnection):
    """
    Class for handling product-category relationships and operations.
    """

    def insert(self,product_name,category_name):
        """
        Inserts a product-category relationship into the database.
        """
        try:
            sql = '''
            INSERT IGNORE INTO product_category(product_id,category_id)
            SELECT p.id,c.id
            FROM products p
            INNER JOIN categories c ON c.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,[category_name,product_name])
            self.commit_and_close()
            return 'product category inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ProductPrice(DatabaseConnection):
    """
    Class for handling product seller price-related operations.
    """

    def insert(self,product_name,material_name,seller_name,price):
        """
        Inserts product seller price details into the database.
        """
        try:
            sql = '''
            INSERT IGNORE INTO product_price(product_id,material_id,seller_id,price)
            SELECT p.id,m.id,s.id,%s
            FROM products p
            INNER JOIN materials m ON m.name = %s
            INNER JOIN sellers s ON s.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,[price,material_name,seller_name,product_name])
            self.commit_and_close()
            return 'product seller price inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ProductTax(DatabaseConnection):
    """
    Class for handling product tax-related operations.
    """

    def insert(self,product_name,material_name,seller_name,tax_rate):
        """
        Inserts product tax details into the database.
        """
        try:
            sql = '''
            INSERT IGNORE INTO product_tax(product_id,material_id,seller_id,tax)
            SELECT p.id,m.id,s.id,%s
            FROM products p
            INNER JOIN materials m ON m.name = %s
            INNER JOIN sellers s ON s.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,[tax_rate,material_name,seller_name,product_name])
            self.commit_and_close()
            return 'product tax inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ProductDiscount(DatabaseConnection):
    """
    Class for handling product discount-related operations.
    """
    def insert(self,product_name,material_name,seller_name,discount_rate):
        """
        Inserts product discount details into the database.
        """
        try:
            sql = '''
            INSERT IGNORE INTO product_discount(product_id,material_id,seller_id,discount)
            SELECT p.id,m.id,s.id,%s
            FROM products p
            INNER JOIN materials m ON m.name = %s
            INNER JOIN sellers s ON s.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,[discount_rate,material_name,seller_name,product_name])
            self.commit_and_close()
            return 'product discount inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
class ProductQuantity(DatabaseConnection):
    """
    Class for handling product quantities and stock management.
    """

    def insert(self,product_name,material_name,seller_name):
        """
        Inserts a product quantity into the database.
        """
        try:
            sql = '''
            INSERT IGNORE INTO product_quantity(product_id,material_id,seller_id)
            SELECT p.id,m.id,s.id
            FROM products p
            INNER JOIN materials m ON m.name = %s
            INNER JOIN sellers s ON s.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,[material_name,seller_name,product_name])
            self.commit_and_close()
            return 'product quantity inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
# Dependency function to verify the API key passed in the request headers
def verify_api_key(x_api_key: str = Header(...)):
     # Compare provided API key with the expected one
    if x_api_key != API_KEY:
        # If the API key is missing or invalid, raise a 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    
# Define a POST endpoint for creating a inventory details
# The route is protected by the API key dependency
@router.post('/product-details/', dependencies=[Depends(verify_api_key)])
def create_profile(inventory: InventoryDetails) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = inventory.dict()
    try:
        product_name = Product().insert(data['product_name'])
        material_name = Material().insert(data['material_name'])
        category_name = Category().insert(data['category_name'])
        seller_name = Seller().insert(data['seller_name'])
        product_category = ProductCategory().insert(data['product_name'],data['category_name'])
        product_quantity = ProductQuantity().insert(
            data['product_name'],data['material_name'],data['seller_name']
        )
        product_seller_price = ProductPrice().insert(
            data['product_name'],data['material_name'],data['seller_name'],data['price']
        )
        product_tax = ProductTax().insert(
            data['product_name'],data['material_name'],data['seller_name'],data['tax_rate']
        )
        product_discount = ProductDiscount().insert(
            data['product_name'],data['material_name'],data['seller_name'],data['discount_rate']
        )

        # Return a success message or result
        return {
            'product message':product_name,
            'material message':material_name,
            'category message':category_name,
            'seller message':seller_name,
            'product category message':product_category,
            'product quantity message':product_quantity,
            'product seller price message':product_seller_price,
            'product tax message':product_tax,
            'product discount message':product_discount
        }
    except Exception as e:
        # In case of any error during insertion, raise a 500 Internal Server Error
        raise HTTPException(status_code=500,detail=str(e))