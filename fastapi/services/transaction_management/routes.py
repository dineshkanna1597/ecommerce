from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
# from decimal import Decimal
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

class PaymentGatewayDetails(BaseModel):
    """
    Pydantic model representing the user profile.

    This model is used to validate and serialize/deserialize the data
    coming from the request body. It ensures that the data conforms to the expected format.
    """
    createdAt: datetime
    transactionId: Optional[str] = None
    orderId: str
    paymentType: str
    paymentMethod: Optional[str] = None
    amount: str
    paymentStatus: str
    processedAt: datetime

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

class PaymentType(DatabaseConnection):
    """
    Class for handling payment type insertions and operations related to payment_type.
    """

    def insert(self,payment_type,created_at):
        """
        Inserts a payment type into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = 'INSERT IGNORE INTO payment_type(payment_types,created_at,last_updated_at) VALUES (%s,%s,%s)'
            self.cursor.execute(sql,(payment_type,created_at,last_updated_at,))
            self.commit_and_close()
            return 'payment type inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class PaymentMethod(DatabaseConnection):
    """
    Class for handling payment method insertions and operations related to payment_method.
    """

    def insert(self,payment_method,created_at):
        """
        Inserts a payment method into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            if payment_method is None:
                return 'payment method is None, skipping insert'
            sql = 'INSERT IGNORE INTO payment_method(payment_methods,created_at,last_updated_at) VALUES (%s,%s,%s)'
            self.cursor.execute(sql,(payment_method,created_at,last_updated_at,))
            self.commit_and_close()
            return 'payment method inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class PaymentStatus(DatabaseConnection):
    """
    Class for handling payment status insertions and operations related to payment_status.
    """

    def insert(self,payment_status,created_at):
        """
        Inserts a payment status into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = 'INSERT IGNORE INTO payment_status(payment_status,created_at,last_updated_at) VALUES (%s,%s,%s)'
            self.cursor.execute(sql,(payment_status,created_at,last_updated_at,))
            self.commit_and_close()
            return 'payment status inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class PaymentTransaction(DatabaseConnection):
    """
    Class for handling payment transaction insertions and operations related to payment_transaction.
    """

    def insert(self,transaction_id,order_id,amount,created_at,
                processed_at,payment_method,payment_status,payment_type):
        """
        Inserts a payment transaction into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''INSERT IGNORE INTO payment_transaction(
            transaction_id,order_id,payment_type_id,payment_method_id,
            amount,payment_status_id,created_at,processed_at,last_updated_at)
            SELECT %s,cso.order_id,pt.id,pm.id,%s,ps.id,%s,%s,%s
            FROM payment_type pt
            INNER JOIN order_management.customer_order cso ON cso.order_id =%s 
            LEFT JOIN payment_method pm ON pm.payment_methods = %s
            INNER JOIN payment_status ps ON ps.payment_status = %s
            WHERE pt.payment_types = %s
            '''
            self.cursor.execute(sql,(transaction_id,amount,created_at,
                                    processed_at,last_updated_at,order_id,payment_method,payment_status,
                                    payment_type,))
            self.commit_and_close()
            return 'payment transaction inserted successfully'
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

@router.post('/payment-gateway/record/', dependencies=[Depends(verify_api_key)])
def payment_gateway_details(gateway_details:PaymentGatewayDetails) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = gateway_details.dict()
    
    transaction_id = data.get('transactionId')
    order_id = data.get('orderId')
    payment_type = data.get('paymentType')
    payment_method = data.get('paymentMethod')
    formatted_amount = data.get('amount')
    amount = float(re.sub(r'[^\d.]', '', formatted_amount))
    payment_status = data.get('paymentStatus')
    created_at = data.get('createdAt')
    processed_at = data.get('processedAt')
        
    # Safely insert each record with error context
    safe_insert("PaymentType", lambda: PaymentType().insert(payment_type, created_at))
    safe_insert("PaymentMethod", lambda: PaymentMethod().insert(payment_method, created_at))
    safe_insert("PaymentStatus", lambda: PaymentStatus().insert(payment_status, created_at))
    safe_insert("PaymentTransaction", lambda: PaymentTransaction().insert(
            transaction_id, order_id, amount, created_at,
            processed_at, payment_method, payment_status, payment_type
        ))        
    return {"message": "Payment details recorded successfully"}

