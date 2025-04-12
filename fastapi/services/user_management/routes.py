from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from datetime import datetime,date
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
            database=os.getenv('MYSQL_DB')  # Target database name
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

class Country(DatabaseConnection):  
    """
    This class extends DatabaseConnection to handle operations 
    related to the 'country table.
    """

    def insert(self, country_name):
        """
        Inserts a new country into the 'country' table.
        
        Args:
            country_name (str): Name of the country to insert.
        
        Returns:
            str: Success or failure message.
        """
        try:
            today = datetime.now()
            sql = 'INSERT INTO country (country_name, last_updated_time) VALUES (%s, %s)'
            self.cursor.execute(sql, (country_name, today))  # Execute the insert query
            self.commit_and_close()  # Commit the transaction and close the connection
            return "Country inserted successfully"
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "Country already available"  # Likely a duplicate entry error

    def fetch_country_id(self, country_name):
        """
        Fetches the country_id for a given country name. If the country does not exist,
        it inserts the country and retrieves the ID.
        
        Args:
            country_name (str): The name of the country to search for.

        Returns:
            int: The country_id if found or newly inserted.
        """
        try:
            sql = 'SELECT country_id FROM country WHERE country_name = %s'
            self.cursor.execute(sql, (country_name,))  # Execute the query
            result = self.cursor.fetchone()  # Fetch one result
            self.conn.close()  # Close the connection

            if result:
                return result[0]  # Return the country_id if found
            else:
                # If the country does not exist, insert it and fetch the ID again
                self.commit_and_close()  # Close previous connection cleanly
                country_obj = Country()  # Create a new instance to insert the country
                country_obj.insert(country_name)  # Insert the country
                country_obj = Country()  # Create a new instance to fetch the country_id
                return country_obj.fetch_country_id(country_name)  # Recursively fetch the ID
        except Exception as e:
            self.conn.close()  # Ensure connection is closed in case of an error
            raise e  # Re-raise the exception for debugging

class State(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'state' table.
    """

    def insert(self, state_name, country_name):
        """
        Inserts a new state into the 'state' table. If the country does not exist, it is inserted first.
        
        Args:
            state_name (str): The name of the state to insert.
            country_name (str): The name of the country the state belongs to.
        
        Returns:
            str: Success or failure message.
        """
        try:
            country_obj = Country()  # Create an instance of the Country class
            country_id = country_obj.fetch_country_id(country_name)  # Get the country ID
            
            today = datetime.now()  # Get the current timestamp
            
            sql = 'INSERT INTO state (state_name, country_id, last_updated_time) VALUES (%s, %s, %s)'
            self.cursor.execute(sql, (state_name, country_id, today))  # Execute the insert query
            
            self.commit_and_close()  # Commit the transaction and close the connection
            return "State and country ID inserted successfully"
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "State and country ID already available"  # Likely a duplicate entry error
    
    def fetch_state_id(self, state_name, country_name):
        """
        Fetches the state_id for a given state and country. If the state does not exist,
        it inserts the state and retrieves the ID.
        
        Args:
            state_name (str): The name of the state to search for.
            country_name (str): The name of the country the state belongs to.

        Returns:
            int: The state_id if found or newly inserted.
        """
        try:
            country_obj = Country()  # Create an instance of the Country class
            country_id = country_obj.fetch_country_id(country_name)  # Get the country ID
            
            sql = 'SELECT state_id FROM state WHERE state_name = %s AND country_id = %s'
            self.cursor.execute(sql, (state_name, country_id))  # Execute the query
            result = self.cursor.fetchone()  # Fetch one result

            if result:
                self.conn.close()  # Close the connection
                return result[0]  # Return the state_id if found
            else:
                # If the state does not exist, insert it and fetch the ID again
                self.commit_and_close()  # Close previous connection cleanly
                state_obj = State()  # Create a new instance to insert the state
                state_obj.insert(state_name, country_name)  # Insert the state
                state_obj = State()  # Create a new instance to fetch the state_id
                return state_obj.fetch_state_id(state_name, country_name)  # Recursively fetch the ID
        except Exception as e:
            self.conn.close()  # Ensure connection is closed in case of an error
            raise e  # Re-raise the exception for debugging

class City(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'city' table.
    """

    def insert(self, city_name, state_name, country_name):
        """
        Inserts a new city into the 'city' table. If the state does not exist, it is inserted first.
        
        Args:
            city_name (str): The name of the city to insert.
            state_name (str): The name of the state the city belongs to.
            country_name (str): The name of the country the state belongs to.
        
        Returns:
            str: Success or failure message.
        """
        try:
            state_obj = State()  # Create an instance of the State class
            state_id = state_obj.fetch_state_id(state_name, country_name)  # Get the state ID
            
            today = datetime.now()  # Get the current timestamp
            
            sql = 'INSERT INTO city (city_name, state_id, last_updated_time) VALUES (%s, %s, %s)'
            self.cursor.execute(sql, (city_name, state_id, today))  # Execute the insert query
            
            self.commit_and_close()  # Commit the transaction and close the connection
            return "City and state ID inserted successfully"
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "City and state ID already available"  # Likely a duplicate entry error
        
    def fetch_city_id(self, city_name, state_name, country_name):
        """
        Fetches the city_id for a given city, state, and country. If the city does not exist,
        it inserts the city and retrieves the ID.
        
        Args:
            city_name (str): The name of the city to search for.
            state_name (str): The name of the state the city belongs to.
            country_name (str): The name of the country the state belongs to.

        Returns:
            int: The city_id if found or newly inserted.
        """
        try:
            state_obj = State()  # Create an instance of the State class
            state_id = state_obj.fetch_state_id(state_name, country_name)  # Get the state ID
            
            sql = 'SELECT city_id FROM city WHERE city_name = %s AND state_id = %s'
            self.cursor.execute(sql, (city_name, state_id))  # Execute the query
            result = self.cursor.fetchone()  # Fetch one result

            if result:
                self.conn.close()  # Close the connection
                return result[0]  # Return the city_id if found
            else:
                # If the city does not exist, insert it and fetch the ID again
                self.commit_and_close()  # Close previous connection cleanly
                city_obj = City()  # Create a new instance to insert the city
                city_obj.insert(city_name, state_name, country_name)  # Insert the city
                city_obj = City()  # Create a new instance to fetch the city_id
                return city_obj.fetch_city_id(city_name, state_name, country_name)  # Recursively fetch the ID
        except Exception as e:
            self.conn.close()  # Ensure connection is closed in case of an error
            raise e  # Re-raise the exception for debugging

class PostalCode(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'postalcode' table.
    """

    def insert(self, postalcode, city_name, state_name, country_name):
        """
        Inserts a new postal code into the 'postalcode' table. If the city does not exist, it is inserted first.
        
        Args:
            postalcode (str): The postal code to insert.
            city_name (str): The name of the city the postal code belongs to.
            state_name (str): The name of the state the city belongs to.
            country_name (str): The name of the country the state belongs to.
        
        Returns:
            str: Success or failure message.
        """
        try:
            city_obj = City()  # Create an instance of the City class
            city_id = city_obj.fetch_city_id(city_name, state_name, country_name)  # Get the city ID
            
            today = datetime.now()  # Get the current timestamp
            
            sql = 'INSERT INTO postalcode (postalcode, city_id, last_updated_time) VALUES (%s, %s, %s)'
            self.cursor.execute(sql, (postalcode, city_id, today))  # Execute the insert query
            
            self.commit_and_close()  # Commit the transaction and close the connection
            return "Postal code and city ID inserted successfully"
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "Postal code and city ID already available"  # Likely a duplicate entry error
    
    def fetch_postalcode_id(self, postalcode, city_name, state_name, country_name):
        """
        Fetches the postalcode_id for a given postal code, city, state, and country. 
        If the postal code does not exist, it inserts the postal code and retrieves the ID.
        
        Args:
            postalcode (str): The postal code to search for.
            city_name (str): The name of the city the postal code belongs to.
            state_name (str): The name of the state the city belongs to.
            country_name (str): The name of the country the state belongs to.

        Returns:
            int: The postalcode_id if found or newly inserted.
        """
        try:
            city_obj = City()  # Create an instance of the City class
            city_id = city_obj.fetch_city_id(city_name, state_name, country_name)  # Get the city ID
            
            sql = 'SELECT postalcode_id FROM postalcode WHERE postalcode = %s AND city_id = %s'
            self.cursor.execute(sql, (postalcode, city_id))  # Execute the query
            result = self.cursor.fetchone()  # Fetch one result

            if result:
                self.conn.close()  # Close the connection
                return result[0]  # Return the postalcode_id if found
            else:
                # If the postal code does not exist, insert it and fetch the ID again
                self.commit_and_close()  # Close previous connection cleanly
                postalcode_obj = PostalCode()  # Create a new instance to insert the postal code
                postalcode_obj.insert(postalcode, city_name, state_name, country_name)  # Insert the postal code
                postalcode_obj = PostalCode()  # Create a new instance to fetch the postalcode_id
                return postalcode_obj.fetch_postalcode_id(postalcode, city_name, state_name, country_name)  # Recursively fetch the ID
        except Exception as e:
            self.conn.close()  # Ensure connection is closed in case of an error
            raise e  # Re-raise the exception for debugging

class Street(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'street' table.
    """

    def insert(self, street_name, postalcode, city_name, state_name, country_name):
        """
        Inserts a new street into the 'street' table. If the postal code does not exist, it is inserted first.
        
        Args:
            street_name (str): The name of the street to insert.
            postalcode (str): The postal code associated with the street.
            city_name (str): The name of the city the street belongs to.
            state_name (str): The name of the state the city belongs to.
            country_name (str): The name of the country the state belongs to.
        
        Returns:
            str: Success or failure message.
        """
        try:
            postalcode_obj = PostalCode()  # Create an instance of the PostalCode class
            postalcode_id = postalcode_obj.fetch_postalcode_id(postalcode, city_name, state_name, country_name)  # Get the postal code ID
            
            today = datetime.now()  # Get the current timestamp
            
            sql = 'INSERT INTO street (street_name, postalcode_id, last_updated_time) VALUES (%s, %s, %s)'
            self.cursor.execute(sql, (street_name, postalcode_id, today))  # Execute the insert query
            
            self.commit_and_close()  # Commit the transaction and close the connection
            return "Street and postal code ID inserted successfully"
        except:
            self.rollback_and_close()  # Rollback in case of an error
            return "Street and postal code ID already available"  # Likely a duplicate entry error
        
    def fetch_street_id(self, street_name, postalcode, city_name, state_name, country_name):
        """
        Fetches the street_id for a given street, postal code, city, state, and country. 
        If the street does not exist, it inserts the street and retrieves the ID.
        
        Args:
            street_name (str): The name of the street to search for.
            postalcode (str): The postal code associated with the street.
            city_name (str): The name of the city the street belongs to.
            state_name (str): The name of the state the city belongs to.
            country_name (str): The name of the country the state belongs to.

        Returns:
            int: The street_id if found or newly inserted.
        """
        try:
            postalcode_obj = PostalCode()  # Create an instance of the PostalCode class
            postalcode_id = postalcode_obj.fetch_postalcode_id(postalcode, city_name, state_name, country_name)  # Get the postal code ID
            
            sql = 'SELECT street_id FROM street WHERE street_name = %s AND postalcode_id = %s'
            self.cursor.execute(sql, (street_name, postalcode_id))  # Execute the query
            result = self.cursor.fetchone()  # Fetch one result

            if result:
                self.conn.close()  # Close the connection
                return result[0]  # Return the street_id if found
            else:
                # If the street does not exist, insert it and fetch the ID again
                self.commit_and_close()  # Close previous connection cleanly
                street_obj = Street()  # Create a new instance to insert the street
                street_obj.insert(street_name, postalcode, city_name, state_name, country_name)  # Insert the street
                street_obj = Street()  # Create a new instance to fetch the street_id
                return street_obj.fetch_street_id(street_name, postalcode, city_name, state_name, country_name)  # Recursively fetch the ID
        except Exception as e:
            self.conn.close()  # Ensure connection is closed in case of an error
            raise e  # Re-raise the exception for debugging

class CustomerBio(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'customer_bio' table.
    """

    def insert(self, customer_data):
        """
        Inserts a new customer record into the 'customer_bio' table.

        Args:
            customer_data (dict): A dictionary containing customer details with the following keys:
                - customer_name (str): The name of the customer.
                - mobile_number (str): The mobile number of the customer.
                - email_id (str): The email address of the customer.
                - dob (str or date): The date of birth of the customer.
                - gender (str): The gender of the customer.

        Returns:
            str: Success message indicating that the customer bio was inserted.
        """
        try:
            today = datetime.now()  # Get the current timestamp
            
            sql = '''
                INSERT INTO customer_bio (customer_name, mobile_number, email_id, dob, gender, last_updated_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            values = (
                customer_data['customer_name'],
                customer_data['mobile_number'],
                customer_data['email_id'],
                customer_data['dob'],
                customer_data['gender'],
                today,
            )

            self.cursor.execute(sql, values)  # Execute the insert query
            self.commit_and_close()  # Commit the transaction and close the connection
            
            return "Customer bio inserted successfully"
        except Exception as e:
            self.rollback_and_close()  # Rollback in case of an error
            raise e  # Re-raise the exception for debugging

    def fetch_customer_id(self, customer_data):
        """
        Fetches the customer_id for a given mobile number and email ID. 
        If the customer does not exist, it inserts the customer and retrieves the ID.

        Args:
            customer_data (dict): A dictionary containing customer details with the following keys:
                - mobile_number (str): The mobile number of the customer.
                - email_id (str): The email address of the customer.

        Returns:
            int: The customer_id if found or newly inserted.
        """
        try:
            sql = 'SELECT customer_id FROM customer_bio WHERE mobile_number = %s AND email_id = %s'
            values = (
                customer_data['mobile_number'],
                customer_data['email_id'],
            )

            self.cursor.execute(sql, values)  # Execute the query
            result = self.cursor.fetchone()  # Fetch one result

            if result:
                self.conn.close()  # Close the connection
                return result[0]  # Return the customer_id if found
            else:
                # If the customer does not exist, insert them and fetch the ID again
                self.commit_and_close()  # Close previous connection cleanly
                customer_obj = CustomerBio()  # Create a new instance to insert the customer
                customer_obj.insert(customer_data)  # Insert the customer
                customer_obj = CustomerBio()  # Create a new instance to fetch the customer_id
                return customer_obj.fetch_customer_id(customer_data)  # Recursively fetch the ID
        except Exception as e:
            self.conn.close()  # Ensure connection is closed in case of an error
            raise e  # Re-raise the exception for debugging

class Address(DatabaseConnection):
    """
    This class extends DatabaseConnection to handle operations related to the 'address' table.
    """

    def insert(self, data):
        """
        Inserts a new address record into the 'address' table.

        Args:
            data (dict): A dictionary containing address-related details with the following keys:
                - customer_name (str): Name of the customer.
                - mobile_number (str): Mobile number of the customer.
                - email_id (str): Email address of the customer.
                - dob (str or date): Date of birth of the customer.
                - gender (str): Gender of the customer.
                - street (str): Street name of the address.
                - postalcode (str): Postal code of the address.
                - city (str): City name of the address.
                - state (str): State name of the address.
                - country (str): Country name of the address.

        Returns:
            str: Success message indicating the data was inserted successfully.
        """
        try:
            today = datetime.now()  # Get the current timestamp

            # Insert customer details and fetch customer_id
            CustomerBio().insert(data)
            customer_id = CustomerBio().fetch_customer_id(data)

            # Insert street details and fetch street_id
            Street().insert(data['street'], data['postalcode'], data['city'], data['state'], data['country'])
            street_id = Street().fetch_street_id(data['street'], data['postalcode'], data['city'], data['state'], data['country'])

            # Insert the complete address into the address table
            sql = '''
            INSERT INTO address (customer_id, street_id, last_updated_time)
            VALUES (%s, %s, %s)
            '''
            self.cursor.execute(sql, (customer_id, street_id, today))
            
            self.commit_and_close()  # Commit the transaction and close the connection
            
            return 'Data Inserted Successfully'
        except Exception as e:
            self.conn.close()  # Ensure connection is closed in case of an error
            raise e  # Re-raise the exception for debugging

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
@router.post('/user-profile/', dependencies=[Depends(verify_api_key)])
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