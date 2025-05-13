from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import random
import requests
import os
from datetime import datetime

# Load environment variables
PAYMENT_URL = f"{os.getenv('API_BASE_URL')}/payment/payment-gateway/generate/"
HEADERS = {"X-API-Key": os.getenv("API_KEY")}

router = APIRouter()

# Define the expected request body using a Pydantic model
class PaymentRequest(BaseModel):
    order_id: str
    order_summary: dict
    shipment_status: str

@router.post("/process")
def process_payment(request: PaymentRequest):
    order_id = request.order_id
    order_summary = request.order_summary
    shipment_status = request.shipment_status

    # Randomly choose payment type and method
    payment_type = random.choice(['prepaid', 'pay on delivery'])
    prepaid_method = random.choice(['credit card', 'debit card', 'upi'])
    pod_method = random.choice(['credit card', 'debit card', 'upi', 'cash'])

    created_at = datetime.now().isoformat()

    try:
        if payment_type == 'pay on delivery':
            if shipment_status == 'Delivered' and pod_method != 'cash':
                payload = {
                    "order_id": str(order_id),
                    "payment_type":'pay on delivery',
                    "payment_method": pod_method,   # e.g., "card", or a token from frontend
                    "amount": order_summary['grandTotal'],  # Convert to smallest currency unit if needed
                    "created_at":created_at
                }
                    
            elif shipment_status == 'Delivered' and pod_method == 'cash':
                payload = {
                    "order_id": str(order_id),
                    "payment_type":'pay on delivery',
                    "payment_method": pod_method,   # e.g., "card", or a token from frontend
                    "amount": order_summary['grandTotal'],  # Convert to smallest currency unit if needed
                    "created_at":created_at
                }
            else:
                payload = {
                    "order_id": str(order_id),
                    "payment_type":'pay on delivery',
                    "payment_method": None,   # e.g., "card", or a token from frontend
                    "amount": order_summary['grandTotal'],  # Convert to smallest currency unit if needed
                    "created_at":created_at
                }
        else:
                payload = {
                    "order_id": str(order_id),
                    "payment_type": 'prepaid',
                    "payment_method": prepaid_method,   # e.g., "card", or a token from frontend
                    "amount": order_summary['grandTotal'],  # Convert to smallest currency unit if needed
                    "created_at":created_at
                }

    # Send payment generation request
        payment_res = requests.post(PAYMENT_URL, json=payload, headers=HEADERS)
        payment_res.raise_for_status()
        payment_data = payment_res.json().get("message")
        return payment_data

    except requests.RequestException as e:
        # Optional: print the response body for debugging
        print(f"Error response: {payment_res.text if 'payment_res' in locals() else str(e)}")
        raise HTTPException(status_code=payment_res.status_code if 'payment_res' in locals() else 500,
                            detail=f"Payment failed: {str(e)}")