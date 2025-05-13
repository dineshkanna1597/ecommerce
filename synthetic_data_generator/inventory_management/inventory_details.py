from dotenv import load_dotenv
from datetime import datetime
import os
import requests
import json

load_dotenv()

data = [
    {
        "product_name": "Chair",
        "material_name": "Wooden",
        "category_name": "Home",
        "seller_name": "Cummings and Sons",
        "price": 887.52,
        "tax_rate": 0.12,
        "discount_rate": 0.05
    },
    {
        "product_name": "Chair",
        "material_name": "Plastic",
        "category_name": "Home",
        "seller_name": "Wise Inc",
        "price": 448.58,
        "tax_rate": 0.12,
        "discount_rate": 0.1
    },
    {
        "product_name": "Chair",
        "material_name": "Metal",
        "category_name": "Home",
        "seller_name": "Becker Ltd",
        "price": 828.61,
        "tax_rate": 0.12,
        "discount_rate": 0.05
    },
    {
        "product_name": "Car",
        "material_name": "Steel",
        "category_name": "Automotive",
        "seller_name": "Jones LLC",
        "price": 114.24,
        "tax_rate": 0.18,
        "discount_rate": 0.0
    },
    {
        "product_name": "Car",
        "material_name": "Plastic",
        "category_name": "Automotive",
        "seller_name": "Gonzalez and Sons",
        "price": 487.94,
        "tax_rate": 0.18,
        "discount_rate": 0.1
    },
    {
        "product_name": "Car",
        "material_name": "Rubber",
        "category_name": "Automotive",
        "seller_name": "Simpson LLC",
        "price": 180.53,
        "tax_rate": 0.18,
        "discount_rate": 0.1
    },
    {
        "product_name": "Computer",
        "material_name": "Plastic",
        "category_name": "Computers",
        "seller_name": "Banks PLC",
        "price": 56.15,
        "tax_rate": 0.15,
        "discount_rate": 0.1
    },
    {
        "product_name": "Computer",
        "material_name": "Metal",
        "category_name": "Computers",
        "seller_name": "Smith Group",
        "price": 64.78,
        "tax_rate": 0.15,
        "discount_rate": 0.05
    },
    {
        "product_name": "Keyboard",
        "material_name": "Plastic",
        "category_name": "Computers",
        "seller_name": "Hayes PLC",
        "price": 41.11,
        "tax_rate": 0.15,
        "discount_rate": 0.1
    },
    {
        "product_name": "Keyboard",
        "material_name": "Metal",
        "category_name": "Computers",
        "seller_name": "Sexton LLC",
        "price": 45.05,
        "tax_rate": 0.15,
        "discount_rate": 0.05
    },
    {
        "product_name": "Mouse",
        "material_name": "Plastic",
        "category_name": "Computers",
        "seller_name": "Crawford Group",
        "price": 60.47,
        "tax_rate": 0.15,
        "discount_rate": 0.1
    },
    {
        "product_name": "Mouse",
        "material_name": "Metal",
        "category_name": "Computers",
        "seller_name": "Thompson Inc",
        "price": 79.2,
        "tax_rate": 0.15,
        "discount_rate": 0.05
    },
    {
        "product_name": "Bike",
        "material_name": "Metal",
        "category_name": "Automotive",
        "seller_name": "Ferguson Group",
        "price": 63.99,
        "tax_rate": 0.18,
        "discount_rate": 0.05
    },
    {
        "product_name": "Bike",
        "material_name": "Rubber",
        "category_name": "Automotive",
        "seller_name": "Wise Inc",
        "price": 54.1,
        "tax_rate": 0.18,
        "discount_rate": 0.1
    },
    {
        "product_name": "Ball",
        "material_name": "Rubber",
        "category_name": "Sports",
        "seller_name": "Henry and Sons",
        "price": 18.35,
        "tax_rate": 0.1,
        "discount_rate": 0.1
    },
    {
        "product_name": "Gloves",
        "material_name": "Rubber",
        "category_name": "Clothing",
        "seller_name": "Mcdonald Ltd",
        "price": 7.97,
        "tax_rate": 0.08,
        "discount_rate": 0.1
    },
    {
        "product_name": "Gloves",
        "material_name": "Soft",
        "category_name": "Clothing",
        "seller_name": "Craig LLC",
        "price": 19.71,
        "tax_rate": 0.08,
        "discount_rate": 0.1
    },
    {
        "product_name": "Gloves",
        "material_name": "Cotton",
        "category_name": "Clothing",
        "seller_name": "Holloway PLC",
        "price": 13.8,
        "tax_rate": 0.08,
        "discount_rate": 0.15
    },
    {
        "product_name": "Pants",
        "material_name": "Cotton",
        "category_name": "Clothing",
        "seller_name": "Obrien and Sons",
        "price": 13.87,
        "tax_rate": 0.08,
        "discount_rate": 0.15
    },
    {
        "product_name": "Shirt",
        "material_name": "Cotton",
        "category_name": "Clothing",
        "seller_name": "Lloyd LLC",
        "price": 13.26,
        "tax_rate": 0.08,
        "discount_rate": 0.15
    },
    {
        "product_name": "Table",
        "material_name": "Wooden",
        "category_name": "Home",
        "seller_name": "Jones LLC",
        "price": 6.78,
        "tax_rate": 0.12,
        "discount_rate": 0.05
    },
    {
        "product_name": "Table",
        "material_name": "Metal",
        "category_name": "Home",
        "seller_name": "Jenkins PLC",
        "price": 5.43,
        "tax_rate": 0.12,
        "discount_rate": 0.05
    },
    {
        "product_name": "Table",
        "material_name": "Granite",
        "category_name": "Home",
        "seller_name": "Ryan Group",
        "price": 12.64,
        "tax_rate": 0.12,
        "discount_rate": 0.05
    },
    {
        "product_name": "Shoes",
        "material_name": "Rubber",
        "category_name": "Shoes",
        "seller_name": "Banks PLC",
        "price": 5.15,
        "tax_rate": 0.08,
        "discount_rate": 0.1
    },
    {
        "product_name": "Hat",
        "material_name": "Cotton",
        "category_name": "Clothing",
        "seller_name": "Banks PLC",
        "price": 16.38,
        "tax_rate": 0.08,
        "discount_rate": 0.15
    },
    {
        "product_name": "Hat",
        "material_name": "Soft",
        "category_name": "Clothing",
        "seller_name": "Ryan Group",
        "price": 19.05,
        "tax_rate": 0.08,
        "discount_rate": 0.1
    },
    {
        "product_name": "Towels",
        "material_name": "Cotton",
        "category_name": "Beauty",
        "seller_name": "Payne LLC",
        "price": 11.1,
        "tax_rate": 0.1,
        "discount_rate": 0.15
    },
    {
        "product_name": "Soap",
        "material_name": "Fresh",
        "category_name": "Health",
        "seller_name": "Johnson PLC",
        "price": 10.36,
        "tax_rate": 0.1,
        "discount_rate": 0.15
    },
    {
        "product_name": "Tuna",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Mcclure Ltd",
        "price": 12.86,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Tuna",
        "material_name": "Frozen",
        "category_name": "Grocery",
        "seller_name": "Gonzalez and Sons",
        "price": 17.36,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Chicken",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Harper PLC",
        "price": 9.81,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Chicken",
        "material_name": "Frozen",
        "category_name": "Grocery",
        "seller_name": "Reese PLC",
        "price": 14.77,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Fish",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Payne LLC",
        "price": 14.95,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Fish",
        "material_name": "Frozen",
        "category_name": "Grocery",
        "seller_name": "Henry and Sons",
        "price": 18.02,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Cheese",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Miller Inc",
        "price": 18.32,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Cheese",
        "material_name": "Frozen",
        "category_name": "Grocery",
        "seller_name": "Miller Inc",
        "price": 18.0,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Bacon",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Simpson LLC",
        "price": 13.69,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Bacon",
        "material_name": "Frozen",
        "category_name": "Grocery",
        "seller_name": "Ferguson Group",
        "price": 18.01,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Pizza",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Wise Inc",
        "price": 19.19,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Pizza",
        "material_name": "Frozen",
        "category_name": "Grocery",
        "seller_name": "Dixon LLC",
        "price": 12.95,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Salad",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Salinas PLC",
        "price": 8.29,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Sausages",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Allen LLC",
        "price": 6.91,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Sausages",
        "material_name": "Frozen",
        "category_name": "Grocery",
        "seller_name": "Richmond and Sons",
        "price": 5.31,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    },
    {
        "product_name": "Chips",
        "material_name": "Fresh",
        "category_name": "Grocery",
        "seller_name": "Allen and Sons",
        "price": 11.89,
        "tax_rate": 0.05,
        "discount_rate": 0.15
    }
]

# Set up request headers, including API key from environment variables
headers = {
    "X-API-Key": os.getenv('API_KEY')
}


base_url = os.getenv("API_BASE_URL")
url = f"{base_url}/inventory/product-details/"

for item in data:
    # Add created_at timestamp
    item["created_at"] = datetime.now().isoformat()
    response = requests.post(url, json=item, headers=headers)
    print('Status Code:', response.status_code)
    try:
        print('Response:', response.json())
    except Exception as e:
        print('Error:', e)
        print('Raw Response:', response.text)

print('Status Code:',response.status_code)
print('Response:',response.json())