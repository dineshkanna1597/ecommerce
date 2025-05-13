from fastapi import FastAPI
from services.user_management.routes import router as user_router
# from services.user_management.user_details import router as user_details
from services.inventory_managment.routes import router as inventory_router
# from services.inventory_managment.inventory_details import router as inventory_details
from services.order_management.routes import router as order_router
# from services.order_management.order_details import router as order_details
# from services.transaction_management.payment_router import router as payment_router
from services.transaction_management.payment_gateway import router as payment_gateway
from services.transaction_management.routes import router as payment_details
# from services.shipping_management.shipment_router import router as shipment_router
from services.shipping_management.shipment_gateway import router as shipment_gateway
from services.shipping_management.routes import router as shipment_details

app = FastAPI()

app.include_router(user_router,prefix='/user')
# app.include_router(user_details,prefix='/user')
app.include_router(inventory_router,prefix='/inventory')
# app.include_router(inventory_details,prefix='/inventory')
app.include_router(order_router,prefix='/order')
# app.include_router(order_details,prefix='/order')
# app.include_router(payment_router,prefix='/payment')
app.include_router(payment_gateway,prefix='/payment')
app.include_router(payment_details,prefix='/payment')
# app.include_router(shipment_router,prefix='/shipment')
app.include_router(shipment_gateway,prefix='/shipment')
app.include_router(shipment_details,prefix='/shipment')