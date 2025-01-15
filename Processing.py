# CARD GUARD
# Data Processing File

# Import Libraries
import psycopg2
import numpy as np
import pandas as pd
import random
import uuid
from faker import Faker

# Define 'Charge' class with all attributes of a charge from the database
class Charge:
    # Initialize all attributes with empty values to detect and handle improper import from database
    def __init__(self, transaction_id="", customer_id="", timestamp=None, merchant_name="", 
                category="", amount=0.00, location="", card_type="", approval_status="", payment_method="", is_fraud="Undetermined"):

        self.transaction_id = transaction_id
        self.customer_id = customer_id
        self.timestamp = timestamp
        self.merchant_name = merchant_name
        self.category = category
        self.amount = amount
        self.location = location
        self.card_type = card_type
        self.approval_status = approval_status
        self.payment_method = payment_method
        self.is_fraud = is_fraud
        
    def print_info(self):
        print(f"Transaction ID: {self.transaction_id}")
        print(f"Customer ID: {self.customer_id}")
        print(f"Timestamp: {self.timestamp}")
        print(f"Merchant Name: {self.merchant_name}")
        print(f"Category: {self.category}")
        print(f"Amount: ${self.amount:.2f}")
        print(f"Location: {self.location}")
        print(f"Card Type: {self.card_type}")
        print(f"Approval Status: {self.approval_status}")
        print(f"Payment Method: {self.payment_method}")
        print(f"Fraud Satus: {self.is_fraud}")

    def set_fraud(self, update):
        self.is_fraud = update

# Function to generate a randomized charge to simulate data from a new charge - returns a Charge
def generate_charge():
    # Initialize Faker instance for generating realistic data
    fake = Faker()

    # Define list of expenditure categories
    categories = [
    "Groceries", "Dining", "Travel", "Retail", "Utilities", "Healthcare",
    "Subscriptions", "Education", "Automobile", "Entertainment", "Charity",
    "Insurance", "Miscellaneous", "Financial Services", "Luxury Items"
    ]
    # Define list of card types
    card_types = ["Visa", "Mastercard", "American Express", "Discover"]
    # Define list of approval statuses
    approval_statuses = ["Approved", "Declined", "Pending"]
    weights = [65, 20, 15]  # Corresponding to 65%, 20%, and 15%
    # Define list of payment methods
    payment_methods = ["Chip", "Swipe", "Contactless", "Online Payment", "Mobile Wallet"]

    # Generate simulated charge information
    transaction_id = str(uuid.uuid4())[:8]
    customer_id = str(uuid.uuid4())[:8]
    timestamp = fake.date_time_this_decade()
    merchant_name = fake.company()
    category = random.choice(categories)
    amount = round(random.uniform(1.0, 5000.0), 2)
    location = f"{fake.city()}, {fake.state_abbr()}"
    card_type = random.choice(card_types)
    approval_status = random.choices(approval_statuses, weights, k=1)[0]
    payment_method = random.choice(payment_methods)
    is_fraud = "Undetermined"

    generated_charge = Charge(transaction_id, customer_id, timestamp, merchant_name, category, amount, location, 
                              card_type, approval_status, payment_method, is_fraud)

    return generated_charge

# Adds a charge to database, allows for manual charge entry
def add_charge(charge):
    # Connect to PostgreSQL Database
    conn = psycopg2.connect(dbname="Credit Card Transactions", user="postgres", password="password123", host="localhost")
    cur = conn.cursor()  # Cursor that allows execution of SQL commands

    try:
        # Check if the transaction_id already exists
        check_sql = "SELECT 1 FROM transactions WHERE transaction_id = %s"
        cur.execute(check_sql, (charge.transaction_id,))
        result = cur.fetchone()

        if result:
            print(f"Transaction ID: {charge.transaction_id} already exists in the database. Skipping insertion.")
        else:
            # SQL to insert new charge
            insert_sql = """
                INSERT INTO transactions (
                    transaction_id, customer_id, timestamp, merchant_name, category, amount, 
                    location, card_type, approval_status, payment_method, is_fraud
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_sql, (
                charge.transaction_id, charge.customer_id, charge.timestamp, 
                charge.merchant_name, charge.category, charge.amount, 
                charge.location, charge.card_type, charge.approval_status, 
                charge.payment_method, charge.is_fraud
            ))
            conn.commit()
            print(f"Transaction ID: {charge.transaction_id} successfully added to database!")

    except Exception as e:
        print("Failed to insert record into table:", e)
        conn.rollback()  # Roll back the transaction in case of an error

    # Close Connection with database
    cur.close()
    conn.close()
    
# Removes a charge from database, allows for manual charge deletion via provided transactionID
def delete_charge(transactionID):
    # Connect to PostgreSQL Database
    conn = psycopg2.connect(dbname="Credit Card Transactions", user="postgres", password="password123", host="localhost")
    cur = conn.cursor() # Cursor that allows execution of SQL commands

    try:
        # Check if the transaction_id exists
        check_sql = "SELECT 1 FROM transactions WHERE transaction_id = %s"
        cur.execute(check_sql, (transactionID,))
        result = cur.fetchone()

        if result:
            # SQL FUNCTION to delete a charge by transaction ID
            remove_sql = "DELETE FROM transactions WHERE transaction_id = %s"
            # Execute the SQL Query
            cur.execute(remove_sql, (transactionID,))
        
            # Commit the deletion
            conn.commit()
            print(f"Transaction ID: {transactionID} successfully removed from database!")

        else:
            print(f"Transaction ID: {transactionID} is not in the database.")     
    
    except Exception as e:
        print(f"Failed to delete record from table: {e}")
        conn.rollback()  # Roll back the transaction in case of an error

    # Close Connection with database
    conn.close()
    cur.close()

# Simulates a new charge being added to database, as if a payment was processed
def swipe_card():
    # Generate a new random charge
    newCharge = generate_charge()
    # Add charge to database with add_charge function
    add_charge(newCharge)

# Function that takes a charge and determines fraudulence based on logic statements
# needs to go through all charges, would be time consuming, should chunk up data, maybe multithread with Pyspark
def flag_fraud(charge):
    # Flag any charge categorized as 'Financial Services'
    if charge.category == "Financial Services":
        charge.set_fraud("Yes")
        print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to [Category: {charge.category}]")
        return True

    # Flag any charge above 3000 that is not categorized as 'Travel' or 'Luxury Items'
    if charge.amount >= 3000.00 and charge.category not in ["Travel, Luxury Items"]:
        charge.set_fraud("Yes")
        print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to [${charge.amount} spent in [Category: {charge.category}]")
        return True
    
    # if two identical charges occur same customer_id

    # if charges occur in a varying location
    
    # If none of the above conditions are met, charge is not fraud
    else:
        charge.set_fraud("No")
        return False

# Testing functions
'''
testCharge = Charge("test")
add_charge(testCharge)
swipe_card()
delete_charge("test")
'''
