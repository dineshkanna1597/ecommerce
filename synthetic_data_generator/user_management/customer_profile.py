from faker import Faker
from dotenv import load_dotenv
import requests
import json
import random
import os

# Load environment variables from a .env file (especially used for API_KEY)
load_dotenv()

class CustomerProfile:
    """
    This class generates fake customer profiles using the Faker library,
    simulating realistic data from various English-speaking countries.
    """

    def __init__(self):
        """
        Initializes the CustomerProfile instance.
        - Defines a list of English locales to simulate different country-specific formats.
        - Randomly selects one locale for each profile.
        - Initializes a Faker instance with that locale.
        """
        self.locales = ['en_AU', 'en_CA', 'en_GB', 'en_IN', 'en_US'] # English-speaking locales
        self.locale = random.choice(self.locales)  # Randomly pick a locale
        self.fake = Faker(self.locale)  # Use Faker with the selected locale

    def customer_phone_number(self):
        """
        Generates a properly formatted international-style phone number
        based on the locale/country.

        Returns:
        str: A phone number with correct country code and structure.
        """
        # Generate a raw phone number with national format using Faker's msisdn()
        raw_number = self.fake.msisdn()

        # Australia: The international format is +61 followed by the last 9 digits.
        if self.locale == 'en_AU':
            return '+61' + raw_number[-9:]  # last 9 digits
        
        # North America: The international format is +1 followed by the last 10 digits.
        elif self.locale in ['en_CA', 'en_US']:
            return '+1' + raw_number[-10:]
        
        # United Kingdom: The international format is +44 followed by the last 10 digits.
        elif self.locale == 'en_GB':
            return '+44' + raw_number[-10:]
        
        # India: The international format is +91 followed by the last 10 digits.
        elif self.locale == 'en_IN':
            return '+91' + raw_number[-10:]
        
        # Fallback: Return the raw number with a '+' prefix.
        return '+' + raw_number  # fallback


    def customer_details(self):
        """
        Generates a fake customer profile with personal and address details.

        Returns:
            dict: A dictionary of fake customer info, including:
                - Name, phone, email, date of birth, gender
                - Country, state, city, postal code, street
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
            'dob': self.fake.date_of_birth(minimum_age=18, maximum_age=100).isoformat(),
            'gender': gender,
            'country': self.fake.current_country(),
            'state': self.fake.administrative_unit(),
            'city': self.fake.city(),
            'postalcode': self.fake.postcode(),
            'street': self.fake.street_address()
        }
    
# Create an instance of the CustomerProfile class    
profile = CustomerProfile()

# Generate a fake customer profile
data = profile.customer_details()

# Set up request headers, including API key from environment variables
headers = {
    "X-API-Key": os.getenv('API_KEY')
}

base_url = os.getenv("API_BASE_URL")
url = f"{base_url}/user/user-details/"

# Send POST request to the server with the generated customer data
response = requests.post(url,json=data,headers=headers)

print('Status Code:',response.status_code)
print('Response:',response.json())