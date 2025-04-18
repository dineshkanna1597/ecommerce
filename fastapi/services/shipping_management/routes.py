from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os
import uuid
import random

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

class ShipmentGateway(BaseModel):
    """
    Pydantic model representing the shipping details.

    This model is used to validate and serialize/deserialize the data
    coming from the request body. It ensures that the data conforms to the expected format.
    """
    orderId: str
    deliveryTo: DeliveryTo

class shipmentProcessing():
    def shipment_status(self,data):
        tracker_id = uuid.uuid4()
        order_id = data['orderId']
        delivery_to = data['deliveryTo']
        shipping_status = 'In Processing'

        return {
            'trackerId':str(tracker_id),
            'orderId':order_id,
            'deliveryTo':delivery_to,
            'status':shipping_status
        }

def verify_api_key(x_api_key: str = Header(...)):
     # Compare provided API key with the expected one
    if x_api_key != API_KEY:
        # If the API key is missing or invalid, raise a 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

# Define a POST endpoint for creating a user profile
# The route is protected by the API key dependency
@router.post('/shipment-details/', dependencies=[Depends(verify_api_key)])
def create_profile(shipment: ShipmentGateway) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = shipment.dict()
    try:
        # Attempt to insert the profile data into the database (or data store)
        result = shipmentProcessing().shipment_status(data)
        # Return a success message or result
        return {'message':result}
    except Exception as e:
        # In case of any error during insertion, raise a 500 Internal Server Error
        raise HTTPException(status_code=500,detail=str(e))