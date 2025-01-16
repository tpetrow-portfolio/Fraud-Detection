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

# Function to update the table with new transaction information when modified
def update_transaction(charge):
    # Connect to PostgreSQL Database
    conn = psycopg2.connect(dbname="Credit Card Transactions", user="postgres", password="password123", host="localhost")
    cur = conn.cursor()  # Cursor that allows execution of SQL commands
    try:
        # SQL query to update row with new transaction information
        update_table_sql = """
                UPDATE transactions
                SET customer_id = %s, timestamp = %s, merchant_name = %s, category = %s, amount = %s, 
                location = %s, card_type = %s, approval_status = %s, payment_method = %s, is_fraud = %s
                WHERE transaction_id = %s
                """
        # Execute the SQL Query
        cur.execute(update_table_sql, (charge.customer_id, charge.timestamp, charge.merchant_name, charge.category, charge.amount, 
                                           charge.location, charge.card_type, charge.approval_status, charge.payment_method, charge.is_fraud,
                                           charge.transaction_id))

        # Check if any rows were affected
        if cur.rowcount == 0:
            print(f"Transaction not found in the database.")
        else:
            print(f"Transaction ID {charge.transaction_id} successfully updated.")
                    
        # Commit the transaction
        conn.commit()
                
    except Exception as e:
        print(f"Error updating transaction {charge.transaction_id}: {e}")
        conn.rollback()  # Roll back in case of an error

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

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
    uuid_list = [str(uuid.uuid4())[:8] for _ in range(5000)] # list of 5000 customer_id's

    # Generate simulated charge information
    transaction_id = str(uuid.uuid4())[:8]
    customer_id = random.choice(uuid_list)
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
            # Execute the SQL Query
            cur.execute(insert_sql, (
                charge.transaction_id, charge.customer_id, charge.timestamp, 
                charge.merchant_name, charge.category, charge.amount, 
                charge.location, charge.card_type, charge.approval_status, 
                charge.payment_method, charge.is_fraud
            ))
            # Commit the addition
            conn.commit()
            print(f"Transaction ID: {charge.transaction_id} successfully added to database!")

    except Exception as e:
        print("Failed to insert record into table:", e)
        conn.rollback()  # Roll back the transaction in case of an error

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
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

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# Simulates a new charge being added to database, as if a payment was processed
def swipe_card():
    # Generate a new random charge
    newCharge = generate_charge()
    # Add charge to database with add_charge function
    add_charge(newCharge)

# Takes in a charge and finds identical charges
def find_repeat_charges(charge):
    # Connect to PostgreSQL Database
    conn = psycopg2.connect(dbname="Credit Card Transactions", user="postgres", password="password123", host="localhost")
    cur = conn.cursor()  # Cursor that allows execution of SQL commands
    try:
        # Check if the transaction_id exists
        check_sql = "SELECT 1 FROM transactions WHERE transaction_id = %s"
        cur.execute(check_sql, (charge.transaction_id,))
        result = cur.fetchone()

        if result:
            # SQL query to find repeat charges
            find_charges_sql = """
                            SELECT *
                            FROM transactions
                            WHERE customer_id = %s
                                AND location = %s
                                AND timestamp != %s
                            """
            # Execute the SQL Query
            cur.execute(find_charges_sql, (charge.customer_id, charge.location, charge.timestamp))
            duplicate_charges = cur.fetchall()

            # Return duplicate charges for further analysis
            # Close Connection with database
            conn.close()
            cur.close()
            return duplicate_charges

        else:
            print(f"Transaction ID: {charge.transaction_id} is not in the database.")
            # Close Connection with database
            conn.close()
            cur.close()
            return []   
    
    except Exception as e:
        print(f"Unable to find transaction: {e}")
        # Close Connection with database
        conn.close()
        cur.close()
        return []
    
    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# Takes in a customer_id and finds the average amount of money spent by customer
def calculate_average_and_std_dev(customerID):
    # Connect to PostgreSQL Database
    conn = psycopg2.connect(dbname="Credit Card Transactions", user="postgres", password="password123", host="localhost")
    cur = conn.cursor()  # Cursor that allows execution of SQL commands
    try:
        # Query to calculate both average and standard deviation in one query
        avg_std_query_sql = """
                    SELECT AVG(amount) AS avg_amount, STDDEV_SAMP(amount) AS std_dev
                    FROM transactions
                    WHERE customer_id = %s
                    """
        # Execute the SQL Query
        cur.execute(avg_std_query_sql, (customerID,))
        result = cur.fetchone()

        # Handle cases where the result might be None
        if result:
            avg_amount = result[0] if result[0] is not None else 0.0
            std_dev = result[1] if result[1] is not None else 0.0
            return avg_amount, std_dev
        else:
            return 0.0, 0.0

    except Exception as e:
        print(f"Error calculating average and standard deviation for customer_id {customerID}: {e}")
        return 0.0, 0.0

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# Function that takes a charge and determines fraudulence based on logic and defined rules
# needs to go through all charges, would be time consuming, should chunk up data, maybe multithread with Pyspark
def flag_fraud(charge):
    try:
        # Check if is_fraud is marked as Undetermined or NULL value
        if charge.is_fraud in ("Undetermined", None):
            # Flag any charge categorized as 'Financial Services' over $1000
            if charge.category == "Financial Services" and charge.amount > 1000.00:
                charge.set_fraud("Fraud")
                print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to [Category: {charge.category}]")
                update_transaction(charge)
                return True

            # Flag any charge above 3000 that is not categorized as 'Travel' or 'Luxury Items'
            if charge.amount > 3000.00 and charge.category not in ["Travel", "Luxury Items"]:
                charge.set_fraud("Fraud")
                print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to [${charge.amount} spent in Category: {charge.category}]")
                update_transaction(charge)
                return True

            # Calculate Z-Score
            avg_spent, std_dev = calculate_average_and_std_dev(charge.customer_id)
            if std_dev > 0:  # Avoid division by zero
                z_score = (charge.amount - avg_spent) / std_dev
            # Flag outliers in customer spending (Z-Score > 2)
            if abs(z_score) > 2.0:
                charge.set_fraud("Fraud")
                print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to outlier in spending. "
                        f"Charge Amount: ${charge.amount}, Z-Score: {z_score:.2f}")
                update_transaction(charge)
                return True

            # Check for identical charges occur with same customer_id, location, and timestamp
            duplicates = find_repeat_charges(charge)
            if duplicates:
                for dup in duplicates:
                    if dup["timestamp"] == charge.timestamp and dup["location"] == charge.location:
                        charge.set_fraud("Fraud")
                        print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to duplicate charge.")
                        update_transaction(charge)
                        return True
            
            # If none of the above conditions are met, mark as Not Fraud
            charge.set_fraud("Not Fraud")
            print(f"Transaction ID: {charge.transaction_id} marked as NOT FRAUD after analysis.")
            update_transaction(charge)
            return False
        
        # If is_fraud is already updated
        else:
            print(f"Transaction ID: {charge.transaction_id} is already set to {charge.is_fraud}")

    except Exception as e:
        print(f"Error processing transaction {charge.transaction_id}: {e}")
        return False

# Testing functions
'''
testCharge = Charge("test")
add_charge(testCharge)
swipe_card()
delete_charge("test")
'''
