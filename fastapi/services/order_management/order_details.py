from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
from babel.numbers import format_currency
from datetime import datetime
import uuid
import random
import requests
import os
import re

load_dotenv()

router = APIRouter()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API_BASE_URL")
HEADERS = {"X-API-Key": API_KEY}

CUSTOMER_URL = f"{BASE_URL}/user/customer-details"
INVENTORY_URL = f"{BASE_URL}/inventory/inventory-details"
ORDER_URL = f"{BASE_URL}/order/order-details/"
UPDATE_URL = f"{BASE_URL}/order/order-details/"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

COUNTRY_CURRENCY = {
    'India': {'locale': 'en_IN', 'currency': 'INR'},
    'United States': {'locale': 'en_US', 'currency': 'USD'},
    'United Kingdom': {'locale': 'en_GB', 'currency': 'GBP'},
    'Canada': {'locale': 'en_CA', 'currency': 'CAD'},
    'Australia': {'locale': 'en_AU', 'currency': 'AUD'}
}

@router.post("/create", dependencies=[Depends(verify_api_key)])
def create_order():
    # Get customer details
    customer_res = requests.get(CUSTOMER_URL, headers=HEADERS)
    if customer_res.status_code != 200:
        raise HTTPException(status_code=customer_res.status_code, detail="Failed to fetch customer details")
    customer = customer_res.json()

    # Get inventory details
    inventory_res = requests.get(INVENTORY_URL, headers=HEADERS)
    if inventory_res.status_code != 200:
        raise HTTPException(status_code=inventory_res.status_code, detail="Failed to fetch inventory")
    inventory_list = inventory_res.json()

    country = customer['address']['country']
    currency = COUNTRY_CURRENCY[country]['currency']
    locale = COUNTRY_CURRENCY[country]['locale']

    # Prepare item list
    items = []
    subtotal = tax_total = discount_total = 0.0

    for item in inventory_list:
        quantity = random.randint(1, 5)
        price = item['price']
        tax = quantity * price * item['tax']
        discount = quantity * price * item['discount']
        total_price = quantity * price

        subtotal += total_price
        tax_total += tax
        discount_total += discount

        items.append({
            'id': item['id'],
            'product': item['product'],
            'material': item['material'],
            'soldBy': item['soldBy'],
            'quantity': quantity,
            'totalPrice': format_currency(total_price, currency, locale=locale),
            'tax': format_currency(tax, currency, locale=locale),
            'discount': format_currency(discount, currency, locale=locale),
        })

    # Final summary
    grand_total = subtotal + tax_total - discount_total
    order_summary = {
        'itemsSubtotal': format_currency(subtotal, currency, locale=locale),
        'tax': format_currency(tax_total, currency, locale=locale),
        'discount': format_currency(discount_total, currency, locale=locale),
        'grandTotal': format_currency(grand_total, currency, locale=locale),
    }

    order_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    payload = {
        'order_id': order_id,
        'customer_id': customer['id'],
        'items': [{'id': i['id'], 'quantity': i['quantity'], 'totalPrice': i['totalPrice']} for i in items],
        'order_summary': order_summary,
        'created_at': created_at
    }

    order_res = requests.post(ORDER_URL, json=payload, headers=HEADERS)
    if order_res.status_code != 200:
        raise HTTPException(status_code=order_res.status_code, detail="Failed to insert order")

    return {
        "order_id":payload.get('order_id'),
        "customer_details":customer,
        'items':payload.get('items'),
        'order_summary':payload.get('order_summary')
        }

@router.patch("/update/{order_id}", dependencies=[Depends(verify_api_key)])
def update_order_status(order_id: str, order_status: str):
    updated_at = datetime.now().isoformat()
    data = {
        'order_id': order_id,
        'order_status': order_status,
        'updated_at': updated_at
    }

    update_res = requests.patch(UPDATE_URL, json=data, headers=HEADERS)
    if update_res.status_code != 200:
        raise HTTPException(status_code=update_res.status_code, detail="Failed to update order status")

    return {"message": "Order status updated", "response": update_res.json()}