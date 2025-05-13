from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
import mysql.connector
import random
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_NAME = "X-API-Key"

router = APIRouter()

class ProductDetail(BaseModel):
    id: int
    product: str
    material: str
    category: str
    soldBy: str
    price: float
    tax: float
    discount: float

# Database connection class
class DatabaseConnection:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('INVENTORY_MANAGEMENT_DB')
        )
        self.cursor = self.conn.cursor()

    def commit_and_close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def rollback_and_close(self):
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

# API key verification
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

# Inventory product details endpoint
@router.get("/inventory-details", response_model=list[ProductDetail], dependencies=[Depends(verify_api_key)])
def get_inventory_details():
    db = DatabaseConnection()
    try:
        product_counts = random.randint(1, 10)
        query = f'''
            SELECT pp.id, products.name, materials.name, categories.name, sellers.name,
                   pp.price, pt.tax, pd.discount
            FROM product_price pp
            INNER JOIN products ON pp.product_id = products.id
            INNER JOIN materials ON pp.material_id = materials.id
            INNER JOIN product_category pc ON products.id = pc.product_id
            INNER JOIN categories ON pc.category_id = categories.id
            INNER JOIN sellers ON pp.seller_id = sellers.id
            INNER JOIN product_tax pt ON pp.id = pt.id
            INNER JOIN product_discount pd ON pp.id = pd.id
            ORDER BY RAND()
            LIMIT {product_counts}
        '''
        db.cursor.execute(query)
        result = db.cursor.fetchall()

        return [{
            'id': row[0],
            'product': row[1],
            'material': row[2],
            'category': row[3],
            'soldBy': row[4],
            'price': float(row[5]),
            'tax': float(row[6]),
            'discount': float(row[7])
        } for row in result]
    except Exception as e:
        db.rollback_and_close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.commit_and_close()