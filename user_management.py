# Import necessary libraries
from dotenv import load_dotenv  # For loading environment variables from a .env file
from faker import Faker  # For generating fake data
from datetime import datetime  # For handling date and time operations
import mysql.connector  # MySQL database connection
import random  # For generating random data
import os  # For accessing environment variables

# Load environment variables from a .env file
load_dotenv()

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

class Country(DatabaseConnection):  
    """
    This class extends DatabaseConnection to handle operations related to the 'country' table.
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
            
            return 'Data Updated Successfully'
        except Exception as e:
            self.conn.close()  # Ensure connection is closed in case of an error
            raise e  # Re-raise the exception for debugging

class CustomerProfile:
    """
    This class generates fake customer profiles using the Faker library.
    """

    def __init__(self):
        """
        Initializes the CustomerProfile class with multiple English locale options.
        A random locale is selected to generate customer details with country-specific formats.
        """
        self.locales = ['en_AU', 'en_CA', 'en_GB', 'en_IN', 'en_US']  # Supported locales
        self.locale = random.choice(self.locales)  # Randomly select one locale
        self.fake = Faker(self.locale)  # Initialize Faker with the selected locale

    def customer_phone_number(self):
        """
        Generates a phone number for the customer, ensuring it has the correct country code.

        Returns:
            str: A formatted phone number with the correct country code.
        """
        phone_number = self.fake.phone_number()

        # Ensure phone numbers start with the correct country code
        if self.locale == 'en_AU' and not phone_number.startswith('+61'):
            return '+61' + phone_number
        elif self.locale in ['en_CA', 'en_US'] and not phone_number.startswith('+1'):
            return '+1' + phone_number
        elif self.locale == 'en_GB' and not phone_number.startswith('+44'):
            return '+44' + phone_number
        elif self.locale == 'en_IN' and not phone_number.startswith('+91'):
            return '+91' + phone_number

        return phone_number  # Return formatted phone number

    def customer_details(self):
        """
        Generates a dictionary containing fake customer details, including personal and address information.

        Returns:
            dict: A dictionary with the following keys:
                - customer_name (str): The name of the customer.
                - mobile_number (str): The mobile number with the appropriate country code.
                - email_id (str): A randomly generated email address.
                - dob (date): A randomly generated date of birth (age 18-100).
                - gender (str): The gender of the customer ('male', 'female', or 'transgender').
                - country (str): The country name.
                - state (str): The state name.
                - city (str): The city name.
                - postalcode (str): The postal code.
                - street (str): The street address.
        """
        gender = random.choice(['male', 'female', 'transgender'])  # Randomly select a gender

        # Assign a name based on gender
        if gender == 'male':
            customer_name = self.fake.name_male()
        elif gender == 'female':
            customer_name = self.fake.name_female()
        else:
            # For transgender, randomly choose between male and female names
            customer_name = random.choice([self.fake.name_male(), self.fake.name_female()])

        return {
            'customer_name': customer_name,
            'mobile_number': self.customer_phone_number(),
            'email_id': self.fake.email(),
            'dob': self.fake.date_of_birth(minimum_age=18, maximum_age=100),
            'gender': gender,
            'country': self.fake.current_country(),
            'state': self.fake.administrative_unit(),
            'city': self.fake.city(),
            'postalcode': self.fake.postcode(),
            'street': self.fake.street_address()
        }

# Example usage:
if __name__ == "__main__":
    customer_profile = CustomerProfile()  # Create an instance of CustomerProfile
    data = customer_profile.customer_details()  # Generate a fake customer profile

    print(Address().insert(data))  # Insert the generated customer details into the database