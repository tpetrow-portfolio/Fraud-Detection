# CARD GUARD
# models.py houses Class definitions

# Import libraries
from datetime import datetime
from utils import highlight

# Define 'Transaction' class with all attributes of a transaction from the database
class Transaction:
    # Initialize all attributes with empty values to detect and handle improper import from database
    def __init__(self, transaction_id="", customer_id="", timestamp=None, merchant_name="", 
                category="", amount=0.00, location="", card_type="", approval_status="", payment_method="", 
                is_fraud="Undetermined", note=None):

        self.transaction_id = transaction_id
        self.customer_id = customer_id
        self.timestamp = timestamp if timestamp is not None else datetime(1970, 1, 1)  # Assign a placeholder timestamp to NULL values for easy identification
        self.merchant_name = merchant_name
        self.category = category
        self.amount = amount
        self.location = location
        self.card_type = card_type
        self.approval_status = approval_status
        self.payment_method = payment_method
        self.is_fraud = is_fraud if is_fraud is not None else "Undetermined"
        self.note = note
        
    def print_info(self):
        print("--------------------------------------------------")
        print(f"Transaction ID: {highlight("blue",self.transaction_id)}")
        print(f"Customer ID: {highlight("blue",self.customer_id)}")
        print(f"Timestamp: {highlight("blue",self.timestamp)}")
        print(f"Merchant Name: {highlight("blue",self.merchant_name)}")
        print(f"Category: {highlight("blue",self.category)}")
        print(f"Amount: {highlight("blue",f'${self.amount:.2f}')}")
        print(f"Location: {highlight("blue",self.location)}")
        print(f"Card Type: {highlight("blue",self.card_type)}")
        print(f"Approval Status: {highlight("blue",self.approval_status)}")
        print(f"Payment Method: {highlight("blue",self.payment_method)}")
        if self.is_fraud == "FRAUD":
            print(f"Fraud Satus: {highlight("red",self.is_fraud)}") # Print FRAUD in red
        elif self.is_fraud == "NOT FRAUD":
            print(f"Fraud Satus: {highlight("green",self.is_fraud)}") # Print NOT FRAUD in green
        else:
            print(f"Fraud Satus: {highlight("blue",self.is_fraud)}") # Print fraud status in default color
        print(f"Transaction Note: {highlight("blue",self.note)}")

    def set_fraud(self, update):
        self.is_fraud = update

    def update_note(self, update):
        self.note = update

# Define 'Customer' class with all attributes of a customer from the database
class Customer:
    # Initialize all attributes with empty values to detect and handle improper import from database
    def __init__(self, customer_id="", first_name="", last_name="", age=0, location="Unknown", phone_number="000-000-0000"):

        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.location = location
        self.phone_number = phone_number
    
        def print_info(self):
            print("--------------------------------------------------")
            print(f"Customer ID: {highlight("blue",self.customer_id)}")
            print(f"Name: {highlight("blue",self.last_name)}, {highlight("blue",self.first_name)}")
            print(f"Age: {highlight("blue",self.age)}")
            print(f"Location: {highlight("blue",self.location)}")
            print(f"Phone Number: {highlight("blue",self.phone_number)}")