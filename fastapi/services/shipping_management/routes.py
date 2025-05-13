from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
# from decimal import Decimal
import mysql.connector
import json
import os

load_dotenv()

# Load the API key from environment variables
API_KEY = os.getenv('API_KEY')

# Define the name of the API key header to be used in requests
API_KEY_NAME = "X-API-Key"

# Initialize an APIRouter instance to register routes
router = APIRouter()

class DeliveryTo(BaseModel):
    """
    Pydantic model representing the delivery details.

    This model is used to validate and serialize/deserialize the data
    coming from the request body. It ensures that the data conforms to the expected format.
    """
    name:str
    mobileNumber:str
    address:str

class PaymentGatewayDetails(BaseModel):
    """
    Pydantic model representing the user profile.

    This model is used to validate and serialize/deserialize the data
    coming from the request body. It ensures that the data conforms to the expected format.
    """
    created_at: datetime
    trackerId: Optional[str] = None
    orderId: str
    deliveryTo: DeliveryTo
    status: Optional[str] = None
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

class ShipmentOrder(DatabaseConnection):
    """
    Class for handling shipment order insertions and operations related to shipment order.
    """

    def insert(self,order_id,delivery_to,created_at):
        """
        Inserts a shipment order into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            # Convert delivery_to (dict) to a JSON string
            delivery_to = json.dumps(delivery_to)

            sql = '''INSERT IGNORE INTO shipment_order(
            order_id,delivery_to,created_at,last_updated_at)
            VALUES (%s,%s,%s,%s)'''
            self.cursor.execute(sql,(order_id,delivery_to,created_at,last_updated_at,))
            self.commit_and_close()
            return 'shipment order inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ShipmentTracker(DatabaseConnection):
    """
    Class for handling shipment tracker insertions and operations related to shipment tracker.
    """

    def insert(self,tracker_id,order_id,created_at):
        """
        Inserts a shipment tracker into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''INSERT IGNORE INTO shipment_tracker(
            tracker_id,shipment_id,created_at,last_updated_at) 
            SELECT %s,shipment_order.id,%s,%s
            FROM shipment_order
            WHERE shipment_order.order_id = %s
            '''
            self.cursor.execute(sql,(tracker_id,created_at,last_updated_at,order_id,))
            self.commit_and_close()
            return 'shipment tracker inserted successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class ShipmentStatus(DatabaseConnection):
    """
    Class for handling shipment status insertions and operations related to shipment status.
    """

    def insert(self,tracker_id,updated_at,shipping_status,created_at):
        """
        Inserts a shipment status into the database.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            sql = '''INSERT IGNORE INTO shipment_status(
            tracker_id,updated_at,shipment_status,created_at,last_updated_at) 
            SELECT st.tracker_id,%s,%s,%s,%s
            FROM shipment_tracker st
            WHERE st.tracker_id = %s
            '''
            self.cursor.execute(sql,(updated_at,shipping_status,created_at,last_updated_at,tracker_id,))
            self.commit_and_close()
            return 'shipment status inserted successfully'
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

@router.post('/shipment-gateway/record/', dependencies=[Depends(verify_api_key)])
def payment_gateway_details(gateway_details:PaymentGatewayDetails) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = gateway_details.dict()
    
    tracker_id = data.get('trackerId')
    order_id = data.get('orderId')
    delivery_to = data.get('deliveryTo')
    shipping_status = data.get('status')
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
        
    # Safely insert each record with error context
    safe_insert("ShipmentOrder", lambda: ShipmentOrder().insert(order_id,delivery_to,created_at))
    safe_insert("ShipmentTracker", lambda: ShipmentTracker().insert(tracker_id,order_id,created_at))
    safe_insert("ShipmentStatus", lambda: ShipmentStatus().insert(tracker_id,updated_at,shipping_status,created_at))
    
    return {"message": "shipment details recorded successfully"}
