from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from datetime import datetime

SHIPMENT_URL = f"{os.getenv('API_BASE_URL')}/shipment/shipment-gateway/generate/"
HEADERS = {"X-API-Key": os.getenv("API_KEY")}

router = APIRouter()

class DeliveryTo(BaseModel):
    name: str
    mobileNumber: str
    address: str

class ShipmentGateway(BaseModel):
    orderId: str
    deliveryTo: DeliveryTo
    created_at: datetime

@router.post("/process")
def generate_shipment(shipment: ShipmentGateway):
    shipment_payload = shipment.dict()
    try:
        shipment_res = requests.post(SHIPMENT_URL, json=shipment_payload, headers=HEADERS)
        shipment_res.raise_for_status()
        shipment_data = shipment_res.json().get("message")
        return shipment_data
    except requests.RequestException as e:
        raise HTTPException(status_code=shipment_res.status_code, detail=f"Shipment failed: {str(e)}")