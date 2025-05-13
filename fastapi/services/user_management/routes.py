from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from datetime import date,datetime
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

# Load the API key from environment variables
API_KEY = os.getenv('API_KEY')

# Define the name of the API key header to be used in requests
API_KEY_NAME = "X-API-Key"

# Initialize an APIRouter instance to register routes
router = APIRouter()

class DatabaseConnection:
    """
    This class handles the database connection and provides methods 
    for committing or rolling back transactions before closing the connection.
    """

    def __init__(self):
        """
        Initializes the database connection using credentials stored in environment variables.
        """
        self.conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),  # Database host (e.g., localhost or an IP address)
            user=os.getenv('MYSQL_USER'),  # Database username
            password=os.getenv('MYSQL_PASSWORD'),  # Database password
            database=os.getenv('USER_MANAGEMENT_DB')  # Target database name
        )
        self.cursor = self.conn.cursor()  # Create a cursor object for executing SQL queries

    def commit_and_close(self):
        """
        Commits the transaction and closes the database connection.
        This should be used when operations are successfully completed.
        """
        self.conn.commit()  # Commit any pending database changes
        self.cursor.close()  # Close the cursor
        self.conn.close()  # Close the database connection

    def rollback_and_close(self):
        """
        Rolls back the transaction and closes the database connection.
        This should be used when an error occurs and changes should not be saved.
        """
        self.conn.rollback()  # Rollback any uncommitted changes
        self.cursor.close()  # Close the cursor
        self.conn.close()  # Close the database connection

class UserProfile(BaseModel):
    """
    Pydantic model representing the user profile.

    This model is used to validate and serialize/deserialize the user's profile data
    coming from the request body. It ensures that the data conforms to the expected format.
    """
    customer_name: str
    mobile_number: str
    email_id: str
    dob: date
    gender: str
    country: str
    state: str
    city: str
    postalcode: str
    street: str
    created_at: datetime

class CustomerBio(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'customer_bio' table.
    """

    def insert(self, data):
        """
        Inserts a new customer record into the 'customer_bio' table.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            query = '''
                INSERT INTO customer_bio (name, mobile_number, email_id, dob, gender,created_at,last_updated_at)
                VALUES (%s, %s, %s, %s, %s, %s,%s)
            '''
            values = (
                data['customer_name'],
                data['mobile_number'],
                data['email_id'],
                data['dob'],
                data['gender'],
                data['created_at'],
                last_updated_at,
            )
            self.cursor.execute(query, values)  # Execute the insert query
            self.commit_and_close()  # Commit the transaction and close the connection
            return "Customer bio inserted successfully"
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e
        
class Country(DatabaseConnection):  
    """
    This class extends DatabaseConnection to handle operations 
    related to the 'country table.
    """

    def insert(self, data):
        """
        Inserts a new country into the 'country' table.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            query = 'INSERT IGNORE INTO country (name,created_at,last_updated_at) VALUES (%s,%s,%s)'
            value = (data['country'],data['created_at'],last_updated_at,)
            self.cursor.execute(query, value)  # Execute the insert query
            self.commit_and_close()  # Commit the transaction and close the connection
            return "Country inserted successfully"
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class State(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'state' table.
    """

    def insert(self, data):
        """
        Inserts a new state into the 'state' table. If the country does not exist, it is inserted first.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            query = '''
            INSERT IGNORE INTO state(name,country_id,created_at,last_updated_at)
            SELECT %s,c.id,%s,%s
            FROM country c
            WHERE c.name = %s
        '''
            values = (
                data['state'],
                data['created_at'],
                last_updated_at,
                data['country'],
            )
            self.cursor.execute(query, values)  # Execute the insert query
            self.commit_and_close()  # Commit the transaction and close the connection
            return "State and country ID inserted successfully"
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class City(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'city' table.
    """

    def insert(self, data):
        """
        Inserts a new city into the 'city' table. If the state does not exist, it is inserted first.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            query = '''
            INSERT IGNORE INTO city(name,state_id,created_at,last_updated_at)
            SELECT %s,s.id,%s,%s
            FROM state s
            INNER JOIN country c ON s.country_id = c.id
            WHERE s.name = %s AND c.name = %s
        '''
            values = (
                data['city'],
                data['created_at'],
                last_updated_at,
                data['state'],
                data['country'],
            )
            self.cursor.execute(query, values)  # Execute the insert query
            self.commit_and_close()  # Commit the transaction and close the connection
            return "City and state ID inserted successfully"
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class PostalCode(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'postalcode' table.
    """
    
    def insert(self, data):
        """
        Inserts a new postal code into the 'postalcode' table. If the city does not exist, it is inserted first.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            query = '''
            INSERT IGNORE INTO postalcode(postalcode,city_id,created_at,last_updated_at)
            SELECT %s, cty.id,%s,%s
            FROM city cty
            INNER JOIN state s ON cty.state_id = s.id
            INNER JOIN country c ON s.country_id = c.id
            WHERE cty.name = %s AND s.name = %s AND c.name = %s
        '''
            values = (
                data['postalcode'],
                data['created_at'],
                last_updated_at,
                data['city'],
                data['state'],
                data['country'],
            )
            self.cursor.execute(query, values)  # Execute the insert query
            
            self.commit_and_close()  # Commit the transaction and close the connection
            return "Postal code and city ID inserted successfully"
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

class Street(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'street' table.
    """

    def insert(self, data):
        """
        Inserts a new street into the 'street' table. If the postal code does not exist, it is inserted first.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            query = '''
            INSERT IGNORE INTO street(name,postalcode_id,created_at,last_updated_at)
            SELECT %s,p.id,%s,%s
            FROM postalcode p
            INNER JOIN city cty ON p.city_id = cty.id
            INNER JOIN state s ON cty.state_id = s.id
            INNER JOIN country c ON s.country_id = c.id
            WHERE p.postalcode = %s AND cty.name = %s AND s.name = %s AND c.name = %s
        '''
            values = (
                data['street'], 
                data['created_at'],
                last_updated_at,
                data['postalcode'], 
                data['city'], 
                data['state'], 
                data['country'],
                )
            self.cursor.execute(query, values)  # Execute the insert query
            self.commit_and_close()  # Commit the transaction and close the connection
            return "Street and postal code ID inserted successfully"
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

def safe_insert(class_name: str, insert_callable):
    try:
        return insert_callable()
    except Exception as e:
        raise Exception(f"[{class_name}] {str(e)}")

class Address(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'address' table.
    """

    def insert(self, data):
        """
        Inserts a new address record into the 'address' table.
        """
        last_updated_at = datetime.now().isoformat()
        try:
            # check customer details
            safe_insert("CustomerBio", lambda: CustomerBio().insert(data))
            # check country details
            safe_insert("Country", lambda: Country().insert(data))
            # check state details
            safe_insert("State", lambda: State().insert(data))
            # check city details
            safe_insert("City", lambda: City().insert(data))
            # check postalcode details
            safe_insert("PostalCode", lambda: PostalCode().insert(data))
            # check street details
            safe_insert("Street", lambda: Street().insert(data))
            # Insert the complete address into the address table
            sql = '''
            INSERT INTO address(customer_id, street_id,created_at,last_updated_at)
            SELECT cb.id,strt.id,%s,%s
            FROM customer_bio cb
            INNER JOIN street strt ON strt.name = %s
            INNER JOIN postalcode p ON strt.postalcode_id = p.id
            INNER JOIN city cty ON p.city_id = cty.id
            INNER JOIN state s ON cty.state_id = s.id
            INNER JOIN country c ON s.country_id = c.id
            WHERE cb.mobile_number = %s AND cb.email_id = %s 
                AND p.postalcode = %s AND cty.name = %s AND s.name = %s AND c.name = %s 
            '''
            values = (
                data['created_at'],
                last_updated_at,
                data['street'],
                data['mobile_number'],
                data['email_id'],
                data['postalcode'],
                data['city'], 
                data['state'], 
                data['country'],
            )
            self.cursor.execute(sql,values)
            
            self.commit_and_close()  # Commit the transaction and close the connection
            
            return 'Data Inserted Successfully'
        except mysql.connector.Error as e:
            self.rollback_and_close()
            raise e

# Dependency function to verify the API key passed in the request headers
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
@router.post('/user-details/', dependencies=[Depends(verify_api_key)])
def create_profile(profile: UserProfile) -> dict:
    # Convert the incoming Pydantic model to a Python dictionary
    data = profile.dict()
    try:
        # Attempt to insert the profile data into the database (or data store)
        result = Address().insert(data)
        # Return a success message or result
        return {'message':result}
    except Exception as e:
        # In case of any error during insertion, raise a 500 Internal Server Error
        raise HTTPException(status_code=500,detail=str(e))