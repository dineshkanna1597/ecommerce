from fastapi import APIRouter, Depends, HTTPException, Header, status
from babel.numbers import format_currency
from dotenv import load_dotenv
from datetime import datetime
import requests
import random
import uuid
import os

load_dotenv()

router = APIRouter()
API_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-Key": os.getenv("API_KEY")}

CUSTOMER_URL = "http://172.16.0.29:8000/user/customer-details"
INVENTORY_URL = "http://172.16.0.29:8000/inventory/inventory-details"
ORDER_URL = "http://172.16.0.29:8000/order/create"
UPDATE_URL = "http://172.16.0.29:8000/order/update/{order_id}"
SHIPMENT_URL = "http://172.16.0.29:8000/shipment/shipment-gateway/generate/"
PAYMENT_URL = "http://172.16.0.29:8000/payment/process"

# Dependency function to verify the API key passed in the request headers
def verify_api_key(x_api_key: str = Header(...)):
     # Compare provided API key with the expected one
    if x_api_key != API_KEY:
        # If the API key is missing or invalid, raise a 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

@router.post("/confirm", dependencies=[Depends(verify_api_key)])
def confirm_order():
    date_time = datetime.now().isoformat()

    # 1. Build order payload
    order_res = requests.post(ORDER_URL, headers=HEADERS)
    if order_res.status_code != 200:
        raise HTTPException(status_code=order_res.status_code, detail="Failed to insert order")
    order = order_res.json()
    order_id = order.get('order_id')
    customer_details = order.get('customer_details')
    customer_name = customer_details.get('name')
    customer_mobile_number = customer_details.get('mobileNumber')
    customer_address = customer_details['address']['fullAddress'] 
    order_items = order.get('items')
    order_summary = order.get('order_summary')
    
    # 3. Generate shipment
    shipment_payload = {
        "orderId": order_id,
        "deliveryTo": {
            "name": customer_name,
            "mobileNumber": customer_mobile_number,
            "address": customer_address
        },
        "created_at": datetime.now().isoformat()
    }

    shipment_res = requests.post(SHIPMENT_URL, json=shipment_payload, headers=HEADERS)
    if shipment_res.status_code != 200:
        raise HTTPException(status_code=shipment_res.status_code, detail="Failed to create shipment")
    shipment_data = shipment_res.json()
    shipment_status = shipment_data.get('shippingStatus')

    # 4. Process payment
    payment_payload = {
        "order_id": order_id,
        "order_summary": order_summary,
        "shipment_status": shipment_status
    }
    payment_res = requests.post(PAYMENT_URL, json=payment_payload,headers=HEADERS)
    if payment_res.status_code != 200:
        raise HTTPException(status_code=payment_res.status_code, detail="Payment failed")
    payment_details = payment_res.json()
    payment_type = payment_details.get('paymentType')
    payment_status = payment_details.get('paymentStatus')

   # 5. Determine order status

    if payment_type == 'prepaid' and payment_status == 'paid':
        order_status = 'Confirmed'
        shipment_details = shipment_data

    elif payment_type == 'prepaid' and payment_status == 'pending':
        order_status = 'Payment on processing. Your order has been pending. Please wait'
        shipment_details = None

    elif payment_type == 'pay on delivery' and payment_status == 'pending':
        order_status = 'Confirmed'
        shipment_details = shipment_data
        
        if shipment_status == 'Delivered':
            payment_res = requests.post(f"{PAYMENT_URL}/payment/process", json=payment_payload, headers=HEADERS)
            if payment_res.status_code == 200:
                payment_details = payment_res.json()

    else:  
        order_status = 'Payment failed. Your order has been cancelled. Please try again.'
        shipment_details = None
    
    # 6. Update Order Status
    update_payload = {
        "order_id": order_id,
        "order_status": order_status,
        "updated_at": date_time
    }
    update_res = requests.patch(UPDATE_URL.replace("{order_id}", order_id), json=update_payload, headers=HEADERS)
    if update_res.status_code != 200:
        raise HTTPException(status_code=update_res.status_code, detail="Failed to update order status")

    # 7. Return Full Order Summary
    return {
        "orderId": order_id,
        "customerDetails": customer_details,
        "orderDetails": {
            "itemsOrdered": order_items,
            "orderSummary": order_summary,
            "orderStatus": order_status,
            "createdAt": date_time
        },
        "paymentDetails": payment_details,
        "shippingDetails": shipment_details
    }