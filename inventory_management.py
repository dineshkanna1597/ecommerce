from dotenv import load_dotenv
from datetime import datetime
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
            database=os.getenv('MYSQL_DB')  # Target database name
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

class Seller(DatabaseConnection):
    def insert(self,seller):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO seller(seller_name,last_updated_time) VALUES (%s,%s)'
            self.cursor.execute(sql,(seller,today))
            self.commit_and_close()
            return 'seller inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "seller already available"  # Likely a duplicate entry error
    def fetch(self):
        pass

class Category(DatabaseConnection):
    def insert(self,category):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO category(category_name,last_updated_time) VALUES (%s,%s)'
            self.cursor.execute(sql,(category,today))
            self.commit_and_close()
            return 'category inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "category already available"  # Likely a duplicate entry error
    def fetch(self):
        pass

class Product(DatabaseConnection):
    def insert(self,product):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO product(product_name,last_updated_time) VALUES (%s,%s)'
            self.cursor.execute(sql,(product,today))
            self.commit_and_close()
            return 'product inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "product already available"  # Likely a duplicate entry error
        
    def fetch(self):
        pass

class Material(DatabaseConnection):
    def insert(self,material):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO material(material_name,last_updated_time) VALUES (%s,%s)'
            self.cursor.execute(sql,(material,today))
            self.commit_and_close()
            return 'material inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "material already available"  # Likely a duplicate entry error
    def fetch(self):
        pass

class ProductCategory(DatabaseConnection):
    def insert(self,product_id,category_id):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO product_category(product_id,category_id,last_updated_time) VALUES (%s,%s,%s)'
            self.cursor.execute(sql,(product_id,category_id,today))
            self.commit_and_close()
            return 'product category inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "product category already available"  # Likely a duplicate entry error
    def fetch(self):
        pass 

class ProductQuantity(DatabaseConnection):
    def insert(self,product_id,material_id,seller_id):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO product_quantity(product_id,material_id,seller_id,quantity,last_updated_time) VALUES (%s,%s,%s,%s,%s)'
            self.cursor.execute(sql,(product_id,material_id,seller_id,100,today))
            self.commit_and_close()
            return 'product quantity inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "product quantity already available"  # Likely a duplicate entry error
    def fetch(self,product_id,material_id,seller_id):
        try:
            sql = 'SELECT quantity FROM product_quantity WHERE product_id = %s AND material_id = %s AND seller_id = %s'
            self.cursor.execute(sql, (product_id, material_id, seller_id))
            quantity = self.cursor.fetchone()[0]
            if quantity == 0:
                quantity = 100
            return quantity
        except Exception as e:
            print(f"Error: {e}")  # Log the error
            return "An error occurred during fetch"

class ProductTax(DatabaseConnection):
    def insert(self,product_id,material_id,seller_id,tax):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO product_tax(product_id,material_id,seller_id,tax,last_updated_time) VALUES(%s,%s,%s,%s,%s)'
            self.cursor.execute(sql,(product_id,material_id,seller_id,tax,today))
            self.commit_and_close()
            return 'product tax inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "product tax already available"  # Likely a duplicate entry error
    def fetch(self):
        pass

class ProductDiscount(DatabaseConnection):
    def insert(self,product_id,material_id,seller_id,discount):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO product_discount(product_id,material_id,seller_id,discount,last_updated_time) VALUES(%s,%s,%s,%s,%s)'
            self.cursor.execute(sql,(product_id,material_id,seller_id,discount,today))
            self.commit_and_close()
            return 'product discount inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "product discount already available"  # Likely a duplicate entry error
    def fetch(self):
        pass

class ProductSellerPrice(DatabaseConnection):
    def insert(self,product_id,material_id,seller_id,price):
        try:
            today = datetime.now()  # Get the current timestamp
            sql = 'INSERT INTO product_seller_price(product_id,material_id,seller_id,price,last_updated_time) VALUES(%s,%s,%s,%s,%s)'
            self.cursor.execute(sql,(product_id,material_id,seller_id,price,today))
            self.commit_and_close()
            return 'product seller price inserted successfully'
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "product seller price already available"  # Likely a duplicate entry error
    def fetch(self):
        pass

class ProductDetails:
    def __init__(self):
        self.data = {
  "seller":['Banks PLC', 'Bridges LLC', 'David PLC', 'Zamora Inc', 'Harper PLC', 'Lloyd LLC', 'Lopez Ltd', 'Obrien and Sons', 'Allen and Sons', 'Evans and Sons', 'Morris Ltd', 'Welch Inc', 'Hayes PLC', 'Johnson PLC', 'Wise Inc', 'Miller Inc', 'Russell PLC', 'Jones LLC', 'Carter Ltd', 'Gonzalez and Sons', 'Smith Group', 'Vang Ltd', 'Campbell Ltd', 'Henry and Sons', 'Crawford Group', 'Salinas PLC', 'Jenkins PLC', 'Payne LLC', 'Mcclure Ltd', 'Sexton LLC', 'Reese PLC', 'Simpson LLC', 'Holloway PLC', 'Robinson Group', 'Becker Ltd', 'Cummings and Sons', 'Ferguson Group', 'Ryan Group', 'Mcdonald Ltd', 'Craig LLC', 'Allen LLC', 'Ho and Sons', 'Thompson PLC', 'Richmond and Sons', 'Dunn and Sons', 'Hall PLC', 'Phillips and Sons', 'Patterson PLC', 'Thompson Inc', 'Dixon LLC'],
  "categories": ["Books", "Movies", "Music", "Games", "Electronics", "Computers", "Home", "Garden", "Tools", "Grocery", "Health", "Beauty", "Toys", "Kids", "Baby", "Clothing", "Shoes", "Jewelery", "Sports", "Outdoors", "Automotive", "Industrial"],
  "materials": ["Steel", "Wooden", "Concrete", "Plastic", "Cotton", "Granite", "Rubber", "Metal", "Soft", "Fresh", "Frozen"],
  "products": ["Chair", "Car", "Computer", "Keyboard", "Mouse", "Bike", "Ball", "Gloves", "Pants", "Shirt", "Table", "Shoes", "Hat", "Towels", "Soap", "Tuna", "Chicken", "Fish", "Cheese", "Bacon", "Pizza", "Salad", "Sausages", "Chips"],
  "product_id": [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 8, 8, 8, 9, 10, 11, 11, 11, 12, 13, 13, 14, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 23, 23, 24],
  "material_id": [2, 4, 8, 1, 4, 7, 4, 8, 4, 8, 4, 8, 8, 7, 7, 7, 9, 5, 5, 5, 2, 8, 6, 7, 5, 9, 5, 10, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 10, 11, 10],
  "category_id": [7, 7, 7, 21, 21, 21, 6, 6, 6, 6, 6, 6, 21, 21, 19, 16, 16, 16, 16, 16, 7, 7, 7, 17, 16, 16, 12, 11, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
  "seller_id": [36, 15, 35, 18, 20, 32, 1, 21, 13, 30, 25, 49, 37, 15, 24, 39, 40, 33, 8, 6, 18, 27, 38, 1, 1, 38, 28, 14, 29, 20, 5, 31, 28, 24, 16, 16, 32, 37, 15, 50, 26, 41, 44, 9],
  "tax_rates": [0.12, 0.12, 0.12, 0.18, 0.18, 0.18, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.18, 0.18, 0.10, 0.08, 0.08, 0.08,0.08, 0.08, 0.12, 0.12, 0.12, 0.08,0.08, 0.08, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05,0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
  "discount_rates": [0.05, 0.10, 0.05, 0.00, 0.10, 0.10, 0.10, 0.05, 0.10, 0.05, 0.10, 0.05,0.05, 0.10, 0.10, 0.10, 0.10, 0.15,0.15, 0.15, 0.05, 0.05, 0.05, 0.10,0.15, 0.10, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,0.15,0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15],
  "prices": [887.52, 448.58, 828.61, 114.24, 487.94, 180.53, 56.15, 64.78, 41.11, 45.05, 60.47, 79.20,63.99, 54.10, 18.35, 7.97, 19.71, 13.80, 13.87, 13.26, 6.78, 5.43, 12.64, 5.15, 16.38,19.05, 11.10, 10.36, 12.86, 17.36, 9.81, 14.77, 14.95, 18.02, 18.32, 18.00, 13.69, 18.01, 19.19, 12.95, 8.29, 6.91, 5.31, 11.89]
}   
    def product_details(self): 
        return {
            'seller_name':self.data['seller'],
            'category_name':self.data['categories'],
            'product_name':self.data['products'],
            'material_name':self.data['materials'],
            'seller_id':self.data['seller_id'],
            'category_id':self.data['category_id'],
            'product_id':self.data['product_id'],
            'material_id':self.data['material_id'],
            'tax':self.data['tax_rates'],
            'discount':self.data['discount_rates'],
            'price':self.data['prices']
        }
    
obj = ProductDetails()
data = obj.product_details()

for product_id,material_id,seller_id,tax,discount in zip(data['product_id'],data['material_id'],data['seller_id'],data['tax'],data['discount']):
    print(ProductTax().insert(product_id,material_id,seller_id,tax))
    print(ProductDiscount().insert(product_id,material_id,seller_id,discount))