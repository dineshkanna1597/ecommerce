from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional
# from decimal import Decimal
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

headers = {
    "X-API-Key": os.getenv('API_KEY')
}

class PaymentGateway(BaseModel):
    """
    Pydantic model representing the user profile.

    This model is used to validate and serialize/deserialize the data
    coming from the request body. It ensures that the data conforms to the expected format.
    """
    order_id: str
    payment_method: Optional[str] = None
    payment_type: str
    amount: str
    created_at:datetime

class PaymentProcessing():
    def payment_status(self,data):
        created_at = data['created_at']
        transaction_id = uuid.uuid4()
        order_id = data['order_id']
        payment_type = data['payment_type']
        payment_method = data['payment_method']
        formatted_amount = data['amount']
        payment_status = random.choice(['pending','paid','failed'])
        processed_at = datetime.now().isoformat()

        if payment_type == 'pay on delivery' and payment_method == 'cash':
            transaction_id = None
            payment_status = 'paid'
        elif payment_type == 'pay on delivery' and payment_method == None:
            transaction_id = None
            payment_status = 'pending'
        else:
            transaction_id = str(transaction_id)

        return {
            'createdAt':created_at.isoformat(),
            'transactionId': transaction_id,
            'orderId':order_id,
            'paymentType':payment_type,
            'paymentMethod':payment_method,
            'amount':formatted_amount,
            'paymentStatus':payment_status,
            'processedAt':processed_at
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
@router.post('/payment-gateway/generate/', dependencies=[Depends(verify_api_key)])
def payment_gateway(payload: PaymentGateway) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = payload.dict()
    
    try:
        # Attempt to insert the profile data into the database (or data store)
        result = PaymentProcessing().payment_status(data)

        base_url = os.getenv("API_BASE_URL")
        response = requests.post(
            f'{base_url}/payment/payment-gateway/record/',
            json=result,
            headers=headers
        )
        return {
            'Status Code': response.status_code,
            'Response': response.json(),
            'message':result
        }
        # Return a success message or result
        #return {'message':result}
    except Exception as e:
        # In case of any error during insertion, raise a 500 Internal Server Error
        #return {'message':result}
        raise HTTPException(status_code=500,detail=str(e))