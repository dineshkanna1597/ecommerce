from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_NAME = "X-API-Key"
router = APIRouter()

class Address(BaseModel):
    street: str
    city: str
    state: str
    postalCode: str
    country: str
    fullAddress: str

class CustomerDetails(BaseModel):
    id: int
    name: str
    mobileNumber: str
    emailId: str
    address: Address

class DatabaseConnection:
    """
    This class handles the database connection and provides methods
    for committing or rolling back transactions before closing the connection.
    """

    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('USER_MANAGEMENT_DB')
        )
        self.cursor = self.conn.cursor()

    def commit_and_close(self):
        """
        Commits the transaction and closes the database connection.
        """
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def rollback_and_close(self):
        """
        Rolls back the transaction and closes the database connection.
        """
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

# Dependency to verify API Key
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

# Automatically validate the API key for every route that depends on this.
@router.get("/customer-details", response_model=CustomerDetails, dependencies=[Depends(verify_api_key)])
def get_customer_details():
    db = DatabaseConnection()
    query = '''
        SELECT customer.id, customer.name, customer.mobile_number, customer.email_id,
               street.name, city.name, state.name, postalcode.postalcode, country.name
        FROM address
        INNER JOIN customer_bio customer ON address.customer_id = customer.id
        INNER JOIN street ON address.street_id = street.id
        INNER JOIN postalcode ON street.postalcode_id = postalcode.id
        INNER JOIN city ON postalcode.city_id = city.id
        INNER JOIN state ON city.state_id = state.id
        INNER JOIN country ON state.country_id = country.id
        ORDER BY RAND()
        LIMIT 1
    '''
    try:
        db.cursor.execute(query)
        result = db.cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="No customer found.")

        return {
            'id': result[0],
            'name': result[1],
            'mobileNumber': result[2],
            'emailId': result[3],
            'address': {
                'street': result[4],
                'city': result[5],
                'state': result[6],
                'postalCode': result[7],
                'country': result[8],
                'fullAddress': f"{result[4]}, {result[5]}, {result[6]}, {result[7]}, {result[8]}"
            }
        }
    except Exception as e:
        db.rollback_and_close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    finally:
        db.commit_and_close()