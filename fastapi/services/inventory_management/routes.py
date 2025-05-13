from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
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
    created_at:datetime

class Product(DatabaseConnection):
    """
    Class for handling product insertions and operations related to products.
    """

    def insert(self,product_name,created_at):
        """
        Inserts a new product into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = 'INSERT IGNORE INTO products(name,created_at,last_updated_at) VALUES (%s,%s,%s)'
            self.cursor.execute(sql,(product_name,created_at,last_updated_at,))
            self.commit_and_close()
            return 'product inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class Material(DatabaseConnection):
    """
    Class for handling material insertions and operations related to materials.
    """

    def insert(self,material_name,created_at):
        """
        Inserts a new material into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = 'INSERT IGNORE INTO materials(name,created_at,last_updated_at) VALUES (%s,%s,%s)'
            self.cursor.execute(sql,(material_name,created_at,last_updated_at,))
            self.commit_and_close()
            return 'material inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class Category(DatabaseConnection):
    """
    A class to manage category insertions into the database.
    """

    def insert(self,category_name,created_at):
        """
        Inserts a new category into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = 'INSERT IGNORE INTO categories(name,created_at,last_updated_at) VALUES (%s,%s,%s)'
            self.cursor.execute(sql,(category_name,created_at,last_updated_at,))
            self.commit_and_close()
            return 'category inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class Seller(DatabaseConnection):
    """
    A class to manage seller insertions into the database.
    """

    def insert(self,seller_name,created_at):
        """
        Inserts a new seller into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = 'INSERT IGNORE INTO sellers(name,created_at,last_updated_at) VALUES (%s,%s,%s)'
            self.cursor.execute(sql,(seller_name,created_at,last_updated_at,))
            self.commit_and_close()
            return 'seller inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ProductCategory(DatabaseConnection):
    """
    Class for handling product-category relationships and operations.
    """

    def insert(self,product_name,category_name,created_at):
        """
        Inserts a product-category relationship into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''
            INSERT IGNORE INTO product_category(product_id,category_id,created_at,last_updated_at)
            SELECT p.id,c.id,%s,%s
            FROM products p
            INNER JOIN categories c ON c.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,(created_at,last_updated_at,category_name,product_name,))
            self.commit_and_close()
            return 'product category inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ProductPrice(DatabaseConnection):
    """
    Class for handling product seller price-related operations.
    """

    def insert(self,product_name,material_name,seller_name,price,created_at):
        """
        Inserts product seller price details into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''
            INSERT IGNORE INTO product_price(product_id,material_id,seller_id,price,created_at,last_updated_at)
            SELECT p.id,m.id,s.id,%s,%s,%s
            FROM products p
            INNER JOIN materials m ON m.name = %s
            INNER JOIN sellers s ON s.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,(price,created_at,last_updated_at,material_name,seller_name,product_name,))
            self.commit_and_close()
            return 'product seller price inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ProductTax(DatabaseConnection):
    """
    Class for handling product tax-related operations.
    """
    
    def insert(self,product_name,material_name,seller_name,tax_rate,created_at):
        """
        Inserts product tax details into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''
            INSERT IGNORE INTO product_tax(product_id,material_id,seller_id,tax,created_at,last_updated_at)
            SELECT p.id,m.id,s.id,%s,%s,%s
            FROM products p
            INNER JOIN materials m ON m.name = %s
            INNER JOIN sellers s ON s.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,(tax_rate,created_at,last_updated_at,material_name,seller_name,product_name,))
            self.commit_and_close()
            return 'product tax inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ProductDiscount(DatabaseConnection):
    """
    Class for handling product discount-related operations.
    """
    def insert(self,product_name,material_name,seller_name,discount_rate,created_at):
        """
        Inserts product discount details into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''
            INSERT IGNORE INTO product_discount(product_id,material_id,seller_id,discount,created_at,last_updated_at)
            SELECT p.id,m.id,s.id,%s,%s,%s
            FROM products p
            INNER JOIN materials m ON m.name = %s
            INNER JOIN sellers s ON s.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,(discount_rate,created_at,last_updated_at,material_name,seller_name,product_name,))
            self.commit_and_close()
            return 'product discount inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
    
class ProductQuantity(DatabaseConnection):
    """
    Class for handling product quantities and stock management.
    """

    def insert(self,product_name,material_name,seller_name,created_at):
        """
        Inserts a product quantity into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''
            INSERT IGNORE INTO product_quantity(product_id,material_id,seller_id,created_at,last_updated_at)
            SELECT p.id,m.id,s.id,%s,%s
            FROM products p
            INNER JOIN materials m ON m.name = %s
            INNER JOIN sellers s ON s.name = %s
            WHERE p.name = %s
        '''
            self.cursor.execute(sql,(created_at,last_updated_at,material_name,seller_name,product_name,))
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
    
def try_insert(class_name: str, insert_callable):
    try:
        return insert_callable()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[{class_name}] {str(e)}")
    
# Define a POST endpoint for creating a inventory details
# The route is protected by the API key dependency
@router.post('/product-details/', dependencies=[Depends(verify_api_key)])
def create_profile(inventory: InventoryDetails) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = inventory.dict()
    return {
        'product message': try_insert("Product", lambda: Product().insert(data['product_name'], data['created_at'])),
        'material message': try_insert("Material", lambda: Material().insert(data['material_name'], data['created_at'])),
        'category message': try_insert("Category", lambda: Category().insert(data['category_name'], data['created_at'])),
        'seller message': try_insert("Seller", lambda: Seller().insert(data['seller_name'], data['created_at'])),
        'product category message': try_insert("ProductCategory", lambda: ProductCategory().insert(
            data['product_name'], data['category_name'], data['created_at'])),
        'product quantity message': try_insert("ProductQuantity", lambda: ProductQuantity().insert(
            data['product_name'], data['material_name'], data['seller_name'], data['created_at'])),
        'product seller price message': try_insert("ProductPrice", lambda: ProductPrice().insert(
            data['product_name'], data['material_name'], data['seller_name'], data['price'], data['created_at'])),
        'product tax message': try_insert("ProductTax", lambda: ProductTax().insert(
            data['product_name'], data['material_name'], data['seller_name'], data['tax_rate'], data['created_at'])),
        'product discount message': try_insert("ProductDiscount", lambda: ProductDiscount().insert(
            data['product_name'], data['material_name'], data['seller_name'], data['discount_rate'], data['created_at']))
    }