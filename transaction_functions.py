# CARD GUARD
# Transaction Functions

# Import libraries
from config import *
from models import *
from utils import *
from customer_functions import find_customer
import random
import uuid
from faker import Faker

# Connect to PostgreSQL Database using the helper function
main_connection = database_connect(**DATABASE_CONFIG)  # Database connection passed into functions
main_cursor = main_connection.cursor()  # Cursor to execute SQL commands passed into functions

# Updates the table with new transaction information when modified
def update_transaction(cursor, transaction):
    try:        
        # SQL query to update row with new transaction information
        update_table_sql = """
                UPDATE {table_name}
                SET customer_id = %s, timestamp = %s, merchant_name = %s, category = %s, amount = %s, 
                    location = %s, card_type = %s, approval_status = %s, payment_method = %s, is_fraud = %s, note = %s
                WHERE transaction_id = %s
                """.format(table_name=TRANSACTIONS_TABLE)
        # Execute the SQL Query
        cursor.execute(update_table_sql, (
            transaction.customer_id, transaction.timestamp, transaction.merchant_name, transaction.category, transaction.amount,
            transaction.location, transaction.card_type, transaction.approval_status, transaction.payment_method, transaction.is_fraud, transaction.note,
            transaction.transaction_id,
        ))
        
        # Commit changes and close connections
        main_connection.commit()
        print(f"Transaction ID: {highlight("blue",transaction.transaction_id)} successfully updated.")
    except Exception as e:
        print(f"Error updating transaction {highlight("blue",transaction.transaction_id)}: {e}")

# Finds a customer's location for detecting locational anomaly fraud
def find_customer_location(cursor, customerID):
    try:
        # Query to find the most common location for the customer
        location_query_sql = """
            SELECT location
            FROM {table_name}
            WHERE customer_id = %s
        """.format(table_name=CUSTOMERS_TABLE)
        # Execute the SQL Query
        cursor.execute(location_query_sql, (customerID,))
        result = cursor.fetchone()

        # Return the customer's common location or 'Unknown' if no result is found
        if result:
            return result[0]
        else:
            return "Unknown"
    
    except Exception as e:
        print(f"Error finding typical location for customer_id {customerID}: {e}")
        return "Unknown"
    
# Helper function to find a customer's age for unexpected category fraud
def find_customer_age(cursor, customerID):
    try:
        # Query to find the customer's age
        age_query_sql = """
            SELECT age
            FROM {table_name}
            WHERE customer_id = %s
        """.format(table_name=CUSTOMERS_TABLE)
        # Execute the SQL Query
        cursor.execute(age_query_sql, (customerID,))
        result = cursor.fetchone()

        # Return the customer's age or 0 if not found
        if result:
            return result[0]
        else:
            return 0
    
    except Exception as e:
        print(f"Error finding typical age for customer_id {customerID}: {e}")
        return 0

# Helper function to find a transaction in database from transaction ID
def find_transaction(cursor, transactionID):
    try:
        # Check if the transaction_id exists
        check_sql = "SELECT * FROM {table_name} WHERE transaction_id = %s".format(table_name=TRANSACTIONS_TABLE)
        cursor.execute(check_sql, (transactionID,))
        
        # Use fetchone to get a single result
        result = cursor.fetchone()

        # Return the result if found, otherwise return None
        if result:
            # Create a Transaction object from the tuple result
            return Transaction(*result)  # Unpacks the result tuple into the Transaction constructor
        else:
            print(f"Transaction ID: {highlight("blue",transactionID)} is not in the database.")
            return None

    except Exception as e:
        print(f"Error finding transaction: {e}")
        raise  # Re-raise the exception for better error propagation

# Adds a transaction to database, allows for manual transaction entry
def add_transaction(cursor, transaction):
    try:
        # Check if the transaction_id already exists
        check_sql = "SELECT 1 FROM {table_name} WHERE transaction_id = %s".format(table_name=TRANSACTIONS_TABLE)
        cursor.execute(check_sql, (transaction.transaction_id,))
        result = cursor.fetchone()

        if result:
            print(f"Transaction ID: {highlight('blue', transaction.transaction_id)} already exists in the database. Skipping insertion.")
        else:
            # SQL to insert new transaction
            insert_sql = """
                INSERT INTO {table_name} (
                    transaction_id, customer_id, timestamp, merchant_name, category, amount, 
                    location, card_type, approval_status, payment_method, is_fraud, note
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """.format(table_name=TRANSACTIONS_TABLE)
            # Execute the SQL Query
            cursor.execute(insert_sql, (
                transaction.transaction_id, transaction.customer_id, transaction.timestamp, 
                transaction.merchant_name, transaction.category, transaction.amount, 
                transaction.location, transaction.card_type, transaction.approval_status, 
                transaction.payment_method, transaction.is_fraud, transaction.note,
            ))
            # Commit the addition
            main_connection.commit()
            print(f"Transaction ID: {highlight('blue', transaction.transaction_id)} successfully added to database!")

    except Exception as e:
        print("Failed to insert record into table:", e)
        main_connection.rollback()  # Roll back the transaction in case of an error
    
# Removes a transaction from database, allows for manual transaction deletion via provided transactionID
def delete_transaction(cursor, transactionID):    
    try:
        # Check if the transaction_id exists
        check_sql = "SELECT 1 FROM {table_name} WHERE transaction_id = %s".format(table_name=TRANSACTIONS_TABLE)
        cursor.execute(check_sql, (transactionID,))
        result = cursor.fetchone()

        if result:
            # SQL FUNCTION to delete a transaction by transaction ID
            remove_sql = "DELETE FROM {table_name} WHERE transaction_id = %s".format(table_name=TRANSACTIONS_TABLE)
            # Execute the SQL Query
            cursor.execute(remove_sql, (transactionID,))
        
            # Commit the deletion
            main_connection.commit()
            print(f"Transaction ID: {highlight("blue",transactionID)} successfully removed from database!")

        else:
            print(f"Transaction ID: {highlight("blue",transactionID)} is not in the database.")
    
    except Exception as e:
        print(f"Failed to delete record from table: {e}")
        main_connection.rollback()  # Roll back the transaction in case of an error

# Function to generate a randomized transaction - returns a Transaction
def generate_transaction(cursor):
    # Initialize Faker instance for generating realistic data
    fake = Faker()

    # Define list of expenditure categories
    categories = [
    "Groceries", "Dining", "Travel", "Retail", "Utilities", "Healthcare",
    "Subscriptions", "Education", "Automobile", "Entertainment", "Charity",
    "Insurance", "Miscellaneous", "Financial Services", "Luxury Items", "Night Club",
    "Bar Service", "Gambling", "Car Rental"
    ]
    card_types = ["Visa", "Mastercard", "American Express", "Discover"]
    approval_statuses = ["Approved", "Declined", "Pending"]
    weights = [75, 10, 15]  # Corresponding to 75%, 10%, and 15%
    payment_methods = ["Chip", "Swipe", "Contactless", "Online Payment", "Mobile Wallet"]
    declined_notes = ["Insufficient Balance", "Expired Card", "Incorrect Security Code", "Card Not Activated", 
                    "Invalid Card Number", "Suspended Card", "Do Not Honor", "Exceeded Credit Limit"]

    # Probability of anomaly (used for location and amount)
    anomaly_chance = 0.02  # 2%

    # Helper function to generate a unique transaction ID
    def generate_unique_transaction_id():
        try:
            while True:
                # Generate a new transaction ID
                transaction_id = str(uuid.uuid4()).replace('-', '')

                # Check if the transaction_id exists
                check_sql = "SELECT 1 FROM {table_name} WHERE transaction_id = %s".format(table_name=TRANSACTIONS_TABLE)
                cursor.execute(check_sql, (transaction_id,))
                result = cursor.fetchone()

                if not result:  # If no match found
                    return transaction_id  # Unique ID found, return it

        except Exception as e:
            print(f"Error generating transaction ID: {e}")
            raise

    # Helper function to generate a customer ID from database
    def fetch_customer():
        try:
            # SQL to fetch a random customer ID from the table
            customer_id_sql = "SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 1".format(table_name=CUSTOMERS_TABLE)
            cursor.execute(customer_id_sql)
            result = cursor.fetchone()

            if result:
                return result
            else:
                raise ValueError("No customer IDs found in the database.")
        except Exception as e:
            print(f"Error generating customer ID: {e}")
            raise

    thisCustomer = Customer(*fetch_customer()) # Unpack fetched customer into new customer object

    # Generate simulated transaction information
    transaction_id = generate_unique_transaction_id()
    customer_id = thisCustomer.customer_id
    timestamp = fake.date_time_this_decade().strftime('%Y-%m-%d %H:%M:%S')
    merchant_name = fake.company()
    category = random.choice(categories)
    if category in ["Night Club", "Bar Service", "Gambling", "Car Rental"]:
        if thisCustomer.age < 21 or thisCustomer.age > 75:
            if random.random() >= anomaly_chance:
                # Skip these categories for customers under 21 or over 75, unless anomaly occurs
                category = random.choice([c for c in categories if c not in ["Night Club", "Bar Service", "Gambling"]])

    if category in ["Groceries", "Utilities", "Charity", "Insurance", "Miscellaneous"]:
        # 2% chance to generate an anomalous value for lower expense categories
        if random.random() < anomaly_chance:
            amount = round(random.uniform(1.0, 5000.0), 2)  # Anomalous range
        else:
            amount = round(random.uniform(10.00, 300.00), 2)  # Normal range
    elif category in ["Dining", "Travel", "Retail", "Healthcare", "Subscriptions", "Education", 
                    "Automobile", "Entertainment", "Luxury Items", "Financial Services"]:
         # 2% chance to generate an anomalous value for higher expense categories
        if random.random() < anomaly_chance:
            amount = round(random.uniform(1.0, 10000.0), 2)  # Anomalous range
        else:
            if category == "Dining":
                amount = round(random.uniform(50.00, 500.00), 2) # Normal range
            elif category == "Travel":
                amount = round(random.uniform(200.00, 3000.00), 2) # Normal range
            elif category == "Retail":
                amount = round(random.uniform(50.00, 500.00), 2) # Normal range
            elif category == "Healthcare":
                amount = round(random.uniform(100.00, 1500.00), 2) # Normal range
            elif category == "Subscriptions":
                amount = round(random.uniform(10.00, 100.00), 2) # Normal range
            elif category == "Education":
                amount = round(random.uniform(100.00, 2500.00), 2) # Normal range
            elif category == "Automobile":
                amount = round(random.uniform(200.00, 1000.00), 2) # Normal range
            elif category == "Entertainment":
                amount = round(random.uniform(20.00, 300.00), 2) # Normal range
            elif category == "Luxury Items":
                amount = round(random.uniform(100.00, 5000.00), 2) # Normal range
            elif category == "Financial Services":
                amount = round(random.uniform(10.00, 200.00), 2) # Normal range
    elif category in ["Night Club", "Bar Service", "Gambling", "Car Rental"]:
        if random.random() < anomaly_chance:
            amount = round(random.uniform(5000.00, 10000.00), 2)  # Anomalous range
        else:
            amount = round(random.uniform(20.00, 500.00), 2)  # Normal for these categories
    # If there's a chance for a new location, simulate it
    if random.random() < anomaly_chance:
        location = f"{fake.city()}, {fake.state_abbr()}"
    else:
        location = thisCustomer.location  # Use the customer's common location
    card_type = random.choice(card_types)
    approval_status = random.choices(approval_statuses, weights, k=1)[0]
    payment_method = random.choice(payment_methods)
    is_fraud = "Undetermined"
    if approval_status == "Declined":
        note = random.choice(declined_notes)
    else:
        note = None 

    generated_transaction = Transaction(transaction_id, customer_id, timestamp, merchant_name, category, amount, location, 
                              card_type, approval_status, payment_method, is_fraud, note)
    
    return generated_transaction

# Simulates a new transaction being added to database, as if a payment was processed
def swipe_card():
    # Generate a new random transaction
    newTransaction = generate_transaction(main_cursor)
    # Add transaction to database with add_transaction function
    add_transaction(main_cursor, newTransaction)
    return newTransaction

# Takes in a transaction and finds identical transactions
def find_repeat_transactions(cursor, transaction):
    try:
        # SQL query to find repeat transactions, and isnt the same transaction as the one being checked
        find_transactions_sql = """
            SELECT transaction_id
            FROM {table_name}
            WHERE customer_id = %s
                AND merchant_name = %s
                AND location = %s
                AND card_type = %s
                AND transaction_id != %s
        """.format(table_name=TRANSACTIONS_TABLE)

        # Execute the SQL query to find duplicate transactions
        cursor.execute(find_transactions_sql, (transaction.customer_id, transaction.merchant_name, transaction.location, transaction.card_type, transaction.transaction_id,))
        duplicate_transactions = cursor.fetchall()
        
        # Return duplicate transactions for further analysis
        return duplicate_transactions

    except Exception as e:
        print(f"Unable to find transaction: {e}")
        return []

# Calculates the average amount of money spent by customer
def calculate_avg_spent(cursor, customerID):
    try:
        # Query to calculate the average spending amount
        avg_query_sql = """
                        SELECT AVG(amount) AS avg_amount
                        FROM {table_name}
                        WHERE customer_id = %s
                        """.format(table_name=TRANSACTIONS_TABLE)
        # Execute the SQL Query
        cursor.execute(avg_query_sql, (customerID,))
        result = cursor.fetchone()

        # Extract the average amount, handling NULL results from the query
        avg_amount = result[0] if result[0] is not None else 0.0
        return avg_amount

    except Exception as e:
        print(f"Error calculating average for customer_id {customerID}: {e}")
        return 0.0

# Takes in a customer_id and finds the average amount of money spent by customer to help with Z-Score
def calculate_average_and_std_dev(cursor, customerID):
    try:
        avg_std_query_sql = """
            SELECT AVG(amount) AS avg_amount, 
                   STDDEV_SAMP(amount) AS std_dev
            FROM {table_name}
            WHERE customer_id = %s AND amount IS NOT NULL
        """.format(table_name=TRANSACTIONS_TABLE)

        cursor.execute(avg_std_query_sql, (customerID,))
        result = cursor.fetchone()

        if result:
            # Ensure values are properly converted to float, handling potential Decimal type
            avg_amount = float(result[0]) if result[0] is not None else 0.0
            std_dev = float(result[1]) if result[1] is not None else 0.0
            return avg_amount, std_dev
        else:
            return 0.0, 0.0

    except Exception as e:
        print(f"Error calculating average and standard deviation for customer_id {customerID}: {e}")
        return 0.0, 0.0

# Checks datetime of each transaction for NULL or placeholder value and asks user to update value
def timestamp_check(cursor):
    try:
        # SQL query to find transactions with placeholder or NULL values
        find_null_timestamps = """
                                SELECT * 
                                FROM {table_name}
                                WHERE timestamp IS NULL OR timestamp = '1970-01-01'
                                """.format(table_name=TRANSACTIONS_TABLE)
        # Execute the SQL Query
        cursor.execute(find_null_timestamps)
        missing_timestamps = cursor.fetchall()

        # If there are missing timestamps, prompt user to update
        if missing_timestamps:
            print(f"Transactions found with NULL or placeholder timestamps.")
            for transaction in missing_timestamps:
                transaction_id = transaction[0]
                print(f"Transaction ID: {highlight("blue",transaction_id)} has a missing timestamp.")
                user_input = input(f"Please enter a valid timestamp for Transaction ID: {highlight("blue",transaction_id)}: ")
                if user_input:
                    try:
                        new_timestamp = datetime.strptime(user_input, '%Y-%m-%d %H:%M:%S')
                        # Update the transaction's timestamp in the database
                        update_sql = """
                            UPDATE {table_name}
                            SET timestamp = %s
                            WHERE transaction_id = %s
                            """.format(table_name=TRANSACTIONS_TABLE)
                        # Execute the SQL Query
                        cursor.execute(update_sql, (new_timestamp, transaction_id,))

                        # Commit the transaction
                        main_connection.commit()
                        print(f"Transaction ID: {highlight("blue",transaction_id)} updated successfully.")
                    except ValueError:
                        print("Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'.")
                else:
                    print(f"No input received for Transaction ID: {highlight("blue",transaction_id)}. Skipping update.")

        else:
            print("No transactions found with missing timestamps.")
                    
    except Exception as e:
        print(f"Error updating transactions: {e}")
        main_connection.rollback()  # Roll back in case of an error

# Helper function to check if a transaction's category is within the expected bounds - returns False if not
def is_amount_valid(transaction):
    category = transaction.category
    amount = transaction.amount

    # Category bounds for each category (including "Other")
    category_bounds = {
        "Groceries": 300.00,
        "Utilities": 300.00,
        "Charity": 300.00,
        "Insurance": 300.00,
        "Miscellaneous": 300.00,
        "Dining": 500.00,
        "Travel": 3000.00,
        "Retail": 500.00,
        "Healthcare": 1500.00,
        "Subscriptions": 100.00,
        "Education": 2500.00,
        "Automobile": 1000.00,
        "Entertainment": 300.00,
        "Luxury Items": 5000.00,
        "Financial Services": 200.00,
        "Night Club": 500.00, 
        "Bar Service": 500.00, 
        "Gambling": 500.00, 
        "Car Rental": 500.00,
        "Other": 500.00  # Max value for unexpected categories
    }

    # Use "Other" as a fallback for any unexpected category
    max_allowed = category_bounds.get(category, category_bounds["Other"])
    
    # If amount is less than or equal to max_allowed, return True
    return amount <= max_allowed

# Notifies customer of 'declined' transaction status note
def notify_customer(cursor, transaction):
    try:
        # SQL query to find declined transactions for the given customer_id
        find_transaction_sql = """
                          SELECT *
                          FROM {table_name}
                          WHERE approval_status = 'Declined' AND customer_id = %s
                          """.format(table_name=TRANSACTIONS_TABLE)
        # Execute the SQL query with customer_id
        cursor.execute(find_transaction_sql, (TRANSACTIONS_TABLE,transaction.customer_id,))
        declined_transactions = cursor.fetchall()

        # If there are declined transactions, print notifications for each
        for declined in declined_transactions:
            transaction_id = declined[0]
            print(f"Transaction ID: {highlight("blue",transaction_id)} Declined. Transaction Note: {transaction.note}")

    except Exception as e:
        print(f"Error retrieving declined transactions for Customer ID: {highlight("blue",transaction.customer_id)}: {e}")

# Main Function that takes a transaction and determines fraudulence based on logic and defined rules
def flag_fraud(cursor, transaction):
    try:
        # Ensure transactions have positive amounts
        if transaction.amount > 0:
            # Check if is_fraud is marked as Undetermined or NULL value
            if transaction.is_fraud in ("Undetermined", None):
                # Apply fraud detection logic only to transactions that are approved or pending
                if transaction.approval_status in ["Pending", "Approved"]:
                    reasons = []  # Collect fraud reasons here
                    fraud_score = 0  # Assignment of a fraud_score based on how many flags are found

                    # FRAUD LOGIC BEGINS
                    # Check for various fraud conditions

                    # If the transaction amount is outside the max bound for the transaction category
                    if not is_amount_valid(transaction):
                        reasons.append(f"Transaction Amount: {highlight('blue', '$')}{highlight('blue', transaction.amount)} out of bounds for Category: {highlight("blue",transaction.category)}")
                        fraud_score += 1

                    # If the transaction amount is outside of the normal standard deviation, based on Z-Score calculation
                    avg_spent, std_dev = calculate_average_and_std_dev(cursor, transaction.customer_id)
                    if std_dev > 0:  # Ensure we don't divide by zero
                        z_score = (float(transaction.amount) - avg_spent) / std_dev
                        if abs(z_score) > 2.0:
                            reasons.append(f"Outlier in spending: Amount {highlight('blue', '$')}{highlight('blue', transaction.amount)}, Z-Score: {highlight('blue', f'{z_score:.2f}')}")
                            fraud_score += 1

                    # If the transaction is identical to another transaction
                    duplicates = find_repeat_transactions(cursor, transaction)
                    if len(duplicates) > 0: # If it finds one or more duplicate transactions, print all duplicate transaction id's
                        reasons.append(f"Duplicate transaction. Found {highlight('blue', len(duplicates))} identical transaction(s): {highlight('blue', ', '.join([dup[0] for dup in duplicates]))}")
                        fraud_score += 1

                    # If the transaction is outside the customer's common location
                    common_location = find_customer_location(cursor, transaction.customer_id)
                    if transaction.location not in [common_location, "Unknown"]:
                        reasons.append(f"Location anomaly: {highlight("blue",transaction.location)} (Expected: {highlight("blue",common_location)})")
                        fraud_score += 1
                    
                    # If the transaction has an unexpected category for customer's age
                    customer_age = find_customer_age(cursor, transaction.customer_id)
                    if customer_age < 21 and transaction.category in ["Night Club", "Bar Service", "Gambling", "Car Rental"]:
                        reasons.append(f"Unexpected Category: {highlight("blue",transaction.category)} for customer's age: {highlight("blue",str(customer_age))}")
                        fraud_score += 1

                    # Set fraud status if any reasons were found, and display all flags to user
                    if reasons:
                        transaction.set_fraud("FRAUD")
                        update_transaction(cursor, transaction)
                        print(f"Transaction ID: {highlight("blue",transaction.transaction_id)} marked as {highlight("red",transaction.is_fraud)} with a fraud score of: {highlight("yellow",fraud_score)} due to the following reasons:")
                        for reason in reasons:
                            print(f"{highlight("blue","-")} {reason}")
                        return fraud_score

                    # If no fraud reasons, mark as Not Fraud
                    transaction.set_fraud("NOT FRAUD")
                    print(f"Transaction ID: {highlight("blue",transaction.transaction_id)} marked as {highlight("green",transaction.is_fraud)} with a fraud score of: {highlight("yellow",fraud_score)} after analysis.")
                    update_transaction(cursor, transaction)
                    return 0
                else:
                    print(f"Transaction ID: {highlight("blue",transaction.transaction_id)} will not be processed. Transaction was marked as {highlight("blue","Declined")}. Declination Note: {highlight("blue",transaction.note)}")
            else:
                if transaction.is_fraud == "FRAUD":
                    print(f"Transaction ID: {highlight("blue",transaction.transaction_id)} will not be processed. Transaction is already set to {highlight("red",transaction.is_fraud)}.")
                else:
                    print(f"Transaction ID: {highlight("blue",transaction.transaction_id)} will not be processed. Transaction is already set to {highlight("green",transaction.is_fraud)}.")
        else:
            print(f"Transaction ID: {highlight("blue",transaction.transaction_id)} can not be processed. Transaction amount is invalid: {highlight("blue",transaction.amount)}")

    except Exception as e:
        print(f"Error processing transaction: {e}")
        main_connection.rollback()
        return False  # Ensure no further processing



# TESTING FRAUD FLAGS

# TEST 1: Amount = 0
'''
print(" ")
print("----------TEST 1----------")
print("  Transaction amount = 0")
print(" ")
testCharge = swipe_card()
testCharge.amount = 0
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''

# TEST 2: is_fraud already set
'''
print(" ")
print("----------TEST 2----------")
print("  is_fraud already set")
print(" ")
testCharge = swipe_card()
testCharge.is_fraud = "FRAUD"
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''

# TEST 3: approval_status = Declined
'''
print(" ")
print("----------TEST 3----------")
print("  approval_status is \'Declined\'")
print(" ")
testCharge = swipe_card()
testCharge.approval_status = "Declined"
testCharge.note = "Invalid Card Number"
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''

# TEST 4: Amount out of expected categorical bounds
'''
print(" ")
print("----------TEST 4----------")
print("  Transaction amount out of expected categorical bounds")
print(" ")
testCharge = swipe_card()
testCharge.approval_status = "Approved"
testCharge.category = "Groceries"
testCharge.amount = 700.00
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''

# TEST 5: Amount out of the ordinary for customer (Z-score > 2)
'''
print(" ")
print("----------TEST 5----------")
print("  Amount out of the ordinary for customer (Z-score > 2)")
print(" ")
testCharge = swipe_card()
testCharge.approval_status = "Approved"
testCharge.category = "Luxury Items"
testCharge.amount = 4999.99
avg_spent, std_dev = calculate_average_and_std_dev(main_cursor,testCharge.customer_id)
z_score = abs((testCharge.amount - avg_spent)/std_dev)
print(f"Average Spent: {avg_spent}. Standard Deviation: {std_dev}. Z-Score of transaction: {z_score:.2f}.")
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''

# TEST 6: Two identical Transactions
'''
print(" ")
print("----------TEST 6----------")
print("  Two identical Transactions")
print(" ")
testCharge1 = swipe_card()
testCharge1.amount = 250.00
testCharge1.approval_status = "Approved"
testCharge1.category = "Groceries"
testCharge2 = swipe_card()
testCharge2.customer_id = testCharge1.customer_id
testCharge2.timestamp = testCharge1.timestamp
testCharge2.merchant_name = testCharge1.merchant_name
testCharge2.category = testCharge1.category
testCharge2.amount = testCharge1.amount
testCharge2.location = testCharge1.location
testCharge2.card_type = testCharge1.card_type
testCharge2.approval_status = testCharge1.approval_status
testCharge2.payment_method = testCharge1.payment_method

flag_fraud(main_cursor, testCharge1) # should be not fraud
flag_fraud(main_cursor, testCharge2) # should be fraud
delete_transaction(main_cursor, testCharge1.transaction_id)
delete_transaction(main_cursor, testCharge2.transaction_id)
'''

# TEST 7: Transaction outside of customer's normal location
'''
print(" ")
print("----------TEST 7----------")
print("  Transaction outside of customer normal location")
print(" ")
testCharge = swipe_card()
testCharge.amount = 250.00
testCharge.approval_status = "Approved"
testCharge.category = "Groceries"
testCharge.location = "London"
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''

# TEST 8: Unexpected category for customer's age
'''
print(" ")
print("----------TEST 8----------")
print("  Unexpected category for customer age")
print(" ")
testCharge = swipe_card()
testCharge.customer_id = "951cfea37" # an existing customer under 21
testCharge.amount = 250.00
testCharge.approval_status = "Approved"
testCharge.category = "Car Rental"
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''

# TEST 9: Three different flags on one transaction
'''
print(" ")
print("----------TEST 9----------")
print("  Three different flags on one transaction")
print(" ")
testCharge = swipe_card()
testCharge.approval_status = "Approved"
testCharge.customer_id = "951cfea37" # an existing customer under 21
testCharge.category = "Car Rental" # age fraud
testCharge.amount = 1000.00 # out of expected bounds for category
testCharge.location = "London" # out of common location
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''

# TEST 10: Non-fraudulent charge
'''
print(" ")
print("----------TEST 10----------")
print("  A Non-fraudulent charge")
print(" ")
testCharge = swipe_card()
testCustomer = find_customer(main_cursor, testCharge.customer_id)
testCharge.amount = 250.00
testCharge.approval_status = "Approved"
testCharge.category = "Groceries"
testCharge.location = testCustomer.location
flag_fraud(main_cursor, testCharge)
delete_transaction(main_cursor, testCharge.transaction_id)
'''












# Close the connection to the PostgreSQL database
database_close(main_connection, main_cursor)