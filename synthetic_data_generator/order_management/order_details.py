from babel.numbers import format_currency
from dotenv import load_dotenv
from datetime import datetime
import mysql.connector
import requests
import random
import uuid
import json
import os
import re

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
            #database=os.getenv('MYSQL_DB')  # Target database name
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

class Customer(DatabaseConnection):
    def customer_details(self):
        query = '''
        SELECT customer.id,customer.name,customer.mobile_number,customer.email_id,
               street.name,city.name,state.name,postalcode.postalcode,country.name
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
        self.cursor.execute('USE user_management')
        self.cursor.execute(query)
        result = self.cursor.fetchone()

        return {
            'id':result[0],
            'name':result[1],
            'mobileNumber':result[2],
            'emailId':result[3],
            'address': {
                'street': result[4],
                'city': result[5],
                'state': result[6],
                'postalCode': result[7],
                'country': result[8],
                'fullAddress': f"{result[4]}, {result[5]}, {result[6]}, {result[7]}, {result[8]}"
    }
        }
        
class Inventory(DatabaseConnection):
    def product_details(self):
        product_counts = random.randint(1,10)
        query = f'''
        SELECT products.name,materials.name,categories.name,sellers.name,
               pp.price,pt.tax,pd.discount
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
        self.cursor.execute('USE inventory_management')
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        return [{
            'product':row[0],
            'material':row[1],
            'category':row[2],
            'soldBy':row[3],
            'price':float(row[4]),
            'tax':float(row[5]),
            'discount':float(row[6])
        }for row in result]

class OrderDetails(DatabaseConnection):
    def __init__(self):
        self.customer_details = Customer().customer_details()
        self.inventory_details = Inventory().product_details()
        self.payment_type = random.choice(['prepaid','pay on delivery'])
        self.prepaid_payment_method = random.choice(['credit card','debit card','upi'])
        self.pod_payment_method = random.choice(['credit card','debit card','upi','cash'])
        self.base_url = os.getenv("API_BASE_URL")
        self.headers = {"X-API-Key": os.getenv('API_KEY')}
        self.payment_url = f"{self.base_url}/payment/payment-details/"
        self.shipment_url = f"{self.base_url}/shipment/shipment-details/"
        self.country = self.customer_details['address']['country']
        self.order_id = None
        self.order_summary = None
        self.items_ordered = None
        self.get_shipment_status = None
        self.country_data = {
            'India': {
                'locale': 'en_IN',
                'currency': 'INR'
            },
            'United States': {
                'locale': 'en_US',
                'currency': 'USD'
            },
            'United Kingdom': {
                'locale': 'en_GB',
                'currency': 'GBP'
            },
            'Canada': {
                'locale': 'en_CA',
                'currency': 'CAD'
            },
            'Australia': {
                'locale': 'en_AU',
                'currency': 'AUD'
            }
        }

    def get_customer_details(self):
        return {
            'name':self.customer_details['name'],
            'mobileNumber':self.customer_details['mobileNumber'],
            'emailId':self.customer_details['emailId'],
            'address':self.customer_details['address']['fullAddress']
        }
    
    def get_item_details(self):
        country = self.country
        currency = self.country_data[country]['currency']
        locale = self.country_data[country]['locale']
        items_ordered = []
        for item in self.inventory_details:
            quantity = random.randint(1, 5)
            price = item['price']
            total_price = round(quantity * price, 2)
            tax = round(quantity * price * item['tax'], 2)
            discount = round(quantity * price * item['discount'], 2)

            formatted_total_price = format_currency(total_price, currency, locale=locale)
            formatted_tax = format_currency(tax, currency, locale=locale)
            formatted_discount = format_currency(discount, currency, locale=locale)
            
            items_ordered.append({
                'product': item['product'],
                'material': item['material'],
                'soldBy': item['soldBy'],
                'quantity': quantity,
                'totalPrice': formatted_total_price,
                'tax': formatted_tax,
                'discount': formatted_discount
            })
        self.items_ordered = items_ordered
        return items_ordered
    
    def calculated_order_summary(self, items_ordered):
        country = self.country
        currency = self.country_data[country]['currency']
        locale = self.country_data[country]['locale']

        subtotal = round(sum(float(re.sub(r'[^\d.]', '', item['totalPrice'])) for item in items_ordered),2)
        formatted_subtotal = format_currency(subtotal, currency, locale=locale)

        tax = round(sum(float(re.sub(r'[^\d.]', '', item['tax'])) for item in items_ordered),2)
        formatted_tax = format_currency(tax, currency, locale=locale)
        
        discount = round(sum(float(re.sub(r'[^\d.]', '', item['discount'])) for item in items_ordered),2)
        formatted_discount = format_currency(discount, currency, locale=locale)
        
        grand_total = round(subtotal + tax - discount, 2)
        formatted_grand_total = format_currency(grand_total, currency, locale=locale)
        
        self.order_summary = {
            'itemsSubtotal': formatted_subtotal,
            'tax': formatted_tax,
            'discount': formatted_discount,
            'grandTotal': formatted_grand_total
        }
        return self.order_summary 

    def get_payment_details(self,shipment_status=None):
     # Send POST request to the server with the generated customer data
        try:
            if self.payment_type == 'pay on delivery':
                if shipment_status == 'Delivered':
                    payload = {
                    "order_id": str(self.order_id),
                    "payment_method": self.pod_payment_method,   # e.g., "card", or a token from frontend
                    "amount": self.order_summary['grandTotal']  # Convert to smallest currency unit if needed
                }
                    
                else:
                    return {
                            "paymentType":self.payment_type,
                            "paymentStatus": "Pending"
                        }
            else:
                payload = {
                    "order_id": str(self.order_id),
                    "payment_method": self.prepaid_payment_method,   # e.g., "card", or a token from frontend
                    "amount": self.order_summary['grandTotal']  # Convert to smallest currency unit if needed
                }

            response = requests.post(self.payment_url,json=payload,headers=self.headers)
            response.raise_for_status()
            response_data = response.json().get("message")

            return {
                    'paymentType':self.payment_type,
                    'paymentMethod': response_data.get('paymentMethod'),
                    'amount': response_data.get('amount'),
                    'paymentStatus': response_data.get('paymentStatus'),
                    'transactionId': response_data.get('transactionId'),
                    'datetime':response_data.get('paymentEnd')
                }
        
        except requests.RequestException as e:
            return {
                'error': str(e)
            }
     
    def get_shipping_details(self):
        order_id = str(self.order_id)
        customer_name = self.get_customer_details().get('name')
        mobile_number = self.get_customer_details().get('mobileNumber')
        address = self.get_customer_details().get('address')
        
        shipment = {
            'orderId':order_id,
            'deliveryTo':{
                'name':customer_name,
                'mobileNumber':mobile_number,
                'address':address
            }
        }
    
        try:
            response = requests.post(self.shipment_url,json=shipment,headers=self.headers)
            response.raise_for_status()
            response_data = response.json().get("message")
    
            return {
            'trackerId':response_data.get('trackerId'),
            'deliveryTo':response_data.get('deliveryTo'),
            'shippingStatus':response_data.get('status')
        }
        except requests.RequestException as e:
            return {
                'error': str(e)
            }
    
    def confirm_order(self):
        self.order_id = uuid.uuid4()
        customer_info = self.get_customer_details()
        items = self.get_item_details()
        summary = self.calculated_order_summary(items)
        payment = self.get_payment_details()
        payment_mode = self.payment_type
        payment_status = payment.get('paymentStatus')

        if payment_mode == 'prepaid' and payment_status == 'success':
            order_status = 'Confirmed'
            shipment_details = self.get_shipping_details()

        elif payment_mode == 'prepaid' and payment_status == 'pending':
            order_status = 'Payment on processing. Your order has been pending. Please wait'
            shipment_details = None

        elif payment_mode == 'pay on delivery' and payment_status == 'Pending':
            order_status = 'Confirmed'
            shipment_details = self.get_shipping_details()
            shipment_status = shipment_details.get('shippingStatus')
            if shipment_status == 'Delivered':
                payment = self.get_payment_details(shipment_status='Delivered')  

        else:  
            order_status = 'Payment failed. Your order has been cancelled. Please try again.'
            shipment_details = None

        return {
            "orderId": str(self.order_id),
            "customerDetails": customer_info,
            "orderDetails": {
                'itemsOrdered': items,
                'orderSummary': summary,
                'orderStatus': order_status
            },
            "paymentDetails": payment,
            "shippingDetails": shipment_details
        }
        
obj = OrderDetails()
processed = obj.confirm_order()

if "error" in processed:
    print("Error:", processed["details"])
else:
    print("Processed message:")
    print(json.dumps(processed, indent=4,ensure_ascii=False))

