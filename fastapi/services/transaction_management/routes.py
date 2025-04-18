from fastapi import APIRouter, Depends, Header, HTTPException, status
from babel.numbers import format_currency
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
# from decimal import Decimal
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

class PaymentGateway(BaseModel):
    """
    Pydantic model representing the user profile.

    This model is used to validate and serialize/deserialize the data
    coming from the request body. It ensures that the data conforms to the expected format.
    """
    order_id: str
    amount: str
    payment_method: str

class PaymentProcessing():
    def payment_status(self,data):
        payment_start = datetime.now()
        transaction_id = uuid.uuid4()
        order_id = data['order_id']
        payment_method = data['payment_method']
        formatted_amount = data['amount']
        amount = float(re.sub(r'[^\d.]', '', formatted_amount))
        payment_status = random.choice(['pending','success','failed'])
        payment_end = datetime.now()

        return {
            'paymentStart':payment_start,
            'transactionId':str(transaction_id),
            'orderId':order_id,
            'paymentMethod':payment_method,
            'amount':formatted_amount,
            'paymentStatus':payment_status,
            'paymentEnd':payment_end
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
@router.post('/payment-details/', dependencies=[Depends(verify_api_key)])
def create_profile(payload: PaymentGateway) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = payload.dict()
    try:
        # Attempt to insert the profile data into the database (or data store)
        result = PaymentProcessing().payment_status(data)
        # Return a success message or result
        return {'message':result}
    except Exception as e:
        # In case of any error during insertion, raise a 500 Internal Server Error
        raise HTTPException(status_code=500,detail=str(e))