from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal
from typing import List
import mysql.connector
import requests
import random
import uuid
import os
import re

load_dotenv()

# Load the API key from environment variables
API_KEY = os.getenv('API_KEY')

# Define the name of the API key header to be used in requests
API_KEY_NAME = "X-API-Key"

# Initialize an APIRouter instance to register routes
router = APIRouter()

class Items(BaseModel):
    id: int
    quantity: int
    totalPrice: str

class OrderSummary(BaseModel):
    itemsSubtotal: str
    tax: str
    discount: str
    grandTotal: str

class OrderDetails(BaseModel):
    """
    Pydantic model representing the user profile.

    This model is used to validate and serialize/deserialize the data
    coming from the request body. It ensures that the data conforms to the expected format.
    """
    order_id: str
    customer_id: int
    items: List[Items]
    order_summary: OrderSummary
    created_at: datetime
    
class OrderStatusRequest(BaseModel):
    order_id: str
    order_status: str
    updated_at: datetime

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

class CustomerOrder(DatabaseConnection):
    """
    Class for handling customer order insertions and operations related to payment_type.
    """

    def insert(self,order_id,customer_id,created_at):
        """
        Inserts a customer order into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''
            INSERT IGNORE INTO customer_order(
            order_id,customer_id,created_at,last_updated_at) 
            SELECT %s,umcb.id,%s,%s
            FROM user_management.customer_bio umcb
            WHERE umcb.id = %s
            '''
            self.cursor.execute(sql,(order_id,created_at,last_updated_at,customer_id,))
            self.commit_and_close()
            return 'customer order inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class OrderProducts(DatabaseConnection):
    """
    Class for handling products ordered insertions and operations related to order products.
    """

    def insert(self,order_id, product_price_id,quantity,total_price,created_at):
        """
        Inserts a order products into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''
            INSERT IGNORE INTO order_products(
            order_id,product_price_id,quantity,total_price,created_at,last_updated_at)
            SELECT order_id,impp.id,%s,%s,%s,%s
            FROM customer_order
            INNER JOIN inventory_management.product_price impp ON impp.id = %s
            WHERE order_id = %s
            '''
            self.cursor.execute(sql,(quantity,total_price,created_at,last_updated_at,product_price_id,order_id,))
            self.commit_and_close()
            return 'order products table inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class OrderStatus(DatabaseConnection):
    """
    Class for handling order status insertions and operations related to order status.
    """

    def insert(self,order_id,updated_at,order_status):
        """
        Inserts a order status into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''
            INSERT IGNORE INTO order_status(
            order_id,updated_at,order_status,last_updated_at)
            SELECT order_id,%s,%s,%s
            FROM customer_order
            WHERE order_id = %s
            '''
            self.cursor.execute(sql,(updated_at,order_status,last_updated_at,order_id,))
            self.commit_and_close()
            return 'order status inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class OrderSummary(DatabaseConnection):
    """
    Class for handling order summary insertions and operations related to order summary.
    """

    def insert(self,order_id,items_subtotal,tax,discount,grand_total,created_at):
        """
        Inserts a order summary into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''INSERT IGNORE INTO order_summary(
            order_id,items_subtotal,tax,discount,grand_total,created_at,last_updated_at)
            SELECT order_id,%s,%s,%s,%s,%s,%s
            FROM customer_order
            WHERE order_id = %s
            '''
            self.cursor.execute(sql,(items_subtotal,tax,discount,grand_total,created_at,
                                     last_updated_at,order_id,))
            self.commit_and_close()
            return 'order summary inserted successfully'
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
    
def safe_insert(class_name: str, insert_callable):
    try:
        return insert_callable()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[{class_name}] {str(e)}")

@router.post('/order-details/', dependencies=[Depends(verify_api_key)])
def order_details(order_details:OrderDetails) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = order_details.dict()
    
    order_id = data.get('order_id')
    customer_id = data.get('customer_id')
    created_at = data.get('created_at')
    # Insert main customer order
    safe_insert("CustomerOrder", lambda: CustomerOrder().insert(
        order_id, customer_id, created_at
    ))

    # Insert each product in the order
    for item in data.get('items'):
        product_price_id = item.get('id')
        quantity = item.get('quantity')
        formatted_total_price = item.get('totalPrice')
        total_price = float(re.sub(r'[^\d.]', '', formatted_total_price))

        safe_insert("OrderProducts", lambda: OrderProducts().insert(
            order_id, product_price_id, quantity, total_price, created_at
        ))


    order_summary = data.get('order_summary')
    formatted_items_subtotal = order_summary.get('itemsSubtotal')
    formatted_tax = order_summary.get('tax')
    formatted_discount = order_summary.get('discount')
    formatted_grand_total = order_summary.get('grandTotal')

    items_subtotal = float(re.sub(r'[^\d.]', '', formatted_items_subtotal)) 
    tax = float(re.sub(r'[^\d.]', '', formatted_tax))
    discount = float(re.sub(r'[^\d.]', '', formatted_discount))
    grand_total = float(re.sub(r'[^\d.]', '', formatted_grand_total))

    safe_insert("OrderSummary",lambda:OrderSummary().insert(
        order_id,items_subtotal,tax,discount,grand_total,created_at
    ))

    return {"message": "Order and products recorded successfully"}

@router.patch("/order-details/", dependencies=[Depends(verify_api_key)])
def order_status(order_status:OrderStatusRequest):
    data = order_status.dict()
    order_id = data.get('order_id')
    updated_at = data.get('updated_at')
    order_status = data.get('order_status')
    
    safe_insert('OrderStatus',lambda:OrderStatus().insert(
        order_id,updated_at,order_status
    ))
    return {"message": "Order status recorded successfully"}