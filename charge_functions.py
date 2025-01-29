# CARD GUARD
# Data Processing File

# Import libraries
import psycopg2
from config import DATABASE_CONFIG, DATABASE_TABLE
import random
from datetime import datetime
import uuid
from faker import Faker

## DATABASE CONNECTION FUNCTIONS
    # Helper function that establishes a connection to the PostgreSQL database
def database_connect(dbname, user, password, host, port=5432):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise

    # Helper function that closes a connection to the PostgreSQL database
def database_close(connection, cursor):
    try:
        # Commit any changes before closing
        if connection:
            connection.commit()  # Only necessary if you’ve made changes to the database
        if cursor:
            cursor.close()
    except Exception as e:
        print(f"Error closing cursor/connection: {e}")
    finally:
        if connection:
            connection.close()

# Connect to PostgreSQL Database using the helper function
main_connection = database_connect(**DATABASE_CONFIG)  # Database connection passed into functions
main_cursor = main_connection.cursor()  # Cursor to execute SQL commands - passed into functions


# Cosmetic function to allow certain text to be highlighted in console
def highlight(color="blue", string=""):
    if color == "blue":
        return f"\033[1;36m{string}\033[0m"  # Highlight text Blue
    elif color == "red":
        return f"\033[1;31m{string}\033[0m"  # Highlight text Red
    elif color == "green":
        return f"\033[1;32m{string}\033[0m"  # Highlight text Green
    else:
        return f"\033[1;36m{string}\033[0m"  # Default to blue if invalid color

# Define 'Charge' class with all attributes of a charge from the database
class Charge:
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

# Updates the table with new transaction information when modified
def update_transaction(connection, cursor, charge):
    try:        
        # SQL query to update row with new transaction information
        update_table_sql = """
                UPDATE {table_name}
                SET customer_id = %s, timestamp = %s, merchant_name = %s, category = %s, amount = %s, 
                    location = %s, card_type = %s, approval_status = %s, payment_method = %s, is_fraud = %s, note = %s
                WHERE transaction_id = %s
                """.format(table_name=DATABASE_TABLE)
        # Execute the SQL Query
        cursor.execute(update_table_sql, (
            charge.customer_id, charge.timestamp, charge.merchant_name, charge.category, charge.amount,
            charge.location, charge.card_type, charge.approval_status, charge.payment_method, charge.is_fraud, charge.note,
            charge.transaction_id,
        ))
        
        # Commit changes and close connections
        connection.commit()
        print(f"Transaction ID: {highlight("blue",charge.transaction_id)} successfully updated.")
    except Exception as e:
        print(f"Error updating transaction {highlight("blue",charge.transaction_id)}: {e}")

# Finds a customer's most common spending location for detecting locational anomaly fraud
def find_typical_location(cursor, customerID):
    try:
        # Query to find the most common location for the customer
        location_query_sql = """
            SELECT location, COUNT(*) AS frequency
            FROM {table_name}
            WHERE customer_id = %s
            GROUP BY location
            ORDER BY frequency DESC
            LIMIT 1;
        """.format(table_name=DATABASE_TABLE)
        # Execute the SQL Query
        cursor.execute(location_query_sql, (customerID,))
        result = cursor.fetchone()

        # Return the most common location or 'Unknown' if no result is found
        if result:
            return result[0]  # The most common location
        else:
            return "Unknown"
    
    except Exception as e:
        print(f"Error finding typical location for customer_id {customerID}: {e}")
        return "Unknown"

# Helper function to find a transaction in database from transaction ID
def find_charge(cursor, transactionID):
    try:
        # Check if the transaction_id exists
        check_sql = "SELECT * FROM {table_name} WHERE transaction_id = %s".format(table_name=DATABASE_TABLE)
        cursor.execute(check_sql, (transactionID,))
        
        # Use fetchone to get a single result
        result = cursor.fetchone()

        # Return the result if found, otherwise return None
        if result:
            # Create a Charge object from the tuple result
            return Charge(*result)  # Unpacks the result tuple into the Charge constructor
        else:
            print(f"Transaction ID: {highlight("blue",transactionID)} is not in the database.")
            return None

    except Exception as e:
        print(f"Error finding transaction: {e}")
        raise  # Re-raise the exception for better error propagation

# Adds a charge to database, allows for manual charge entry
def add_charge(cursor, charge):
    try:
        # Check if the transaction_id already exists
        check_sql = "SELECT 1 FROM {table_name} WHERE transaction_id = %s".format(table_name=DATABASE_TABLE)
        cursor.execute(check_sql, (charge.transaction_id,))
        result = cursor.fetchone()

        if result:
            print(f"Transaction ID: {highlight('blue', charge.transaction_id)} already exists in the database. Skipping insertion.")
        else:
            # SQL to insert new charge
            insert_sql = """
                INSERT INTO {table_name} (
                    transaction_id, customer_id, timestamp, merchant_name, category, amount, 
                    location, card_type, approval_status, payment_method, is_fraud, note
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """.format(table_name=DATABASE_TABLE)
            # Execute the SQL Query
            cursor.execute(insert_sql, (
                charge.transaction_id, charge.customer_id, charge.timestamp, 
                charge.merchant_name, charge.category, charge.amount, 
                charge.location, charge.card_type, charge.approval_status, 
                charge.payment_method, charge.is_fraud, charge.note,
            ))
            # Commit the addition
            print(f"Transaction ID: {highlight('blue', charge.transaction_id)} successfully added to database!")

    except Exception as e:
        print("Failed to insert record into table:", e)
        if main_connection:
            main_connection.rollback()  # Roll back the transaction in case of an error
    
# Removes a charge from database, allows for manual charge deletion via provided transactionID
def delete_charge(cursor, transactionID):    
    try:
        # Check if the transaction_id exists
        check_sql = "SELECT 1 FROM {table_name} WHERE transaction_id = %s".format(table_name=DATABASE_TABLE)
        cursor.execute(check_sql, (transactionID,))
        result = cursor.fetchone()

        if result:
            # SQL FUNCTION to delete a charge by transaction ID
            remove_sql = "DELETE FROM {table_name} WHERE transaction_id = %s".format(table_name=DATABASE_TABLE)
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

# Function to generate a randomized charge to simulate data from a new charge - returns a Charge
def generate_charge(cursor):

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
    weights = [75, 10, 15]  # Corresponding to 75%, 10%, and 15%
    # Define list of payment methods
    payment_methods = ["Chip", "Swipe", "Contactless", "Online Payment", "Mobile Wallet"]
    declined_notes = ["Insufficient Balance", "Expired Card", "Incorrect CVV", "Card Not Activated", 
                  "Invalid Card Number", "Suspended Card", "Do Not Honor", "Exceeded Credit Limit"]
    uuid_list = [str(uuid.uuid4())[:8] for _ in range(4000)] # list of 4000 customer_id's

    # Probability of anomaly (used for location and amount)
    anomaly_chance = 0.02  # 2%

    # Helper function to generate a unique transaction ID
    def generate_unique_transaction_id():
        try:
            while True:
                # Generate a new transaction ID
                transaction_id = str(uuid.uuid4()).replace('-', '')

                # Check if the transaction_id exists
                check_sql = "SELECT 1 FROM {table_name} WHERE transaction_id = %s".format(table_name=DATABASE_TABLE)
                cursor.execute(check_sql, (transaction_id,))
                result = cursor.fetchone()

                if not result:  # If no match found
                    return transaction_id  # Unique ID found, return it

        except Exception as e:
            print(f"Error generating transaction ID: {e}")
            raise

    # Generate simulated charge information
    transaction_id = generate_unique_transaction_id()
    customer_id = random.choice(uuid_list)
    timestamp = fake.date_time_this_decade()
    merchant_name = fake.company()
    category = random.choice(categories)
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
                amount = round(random.uniform(50.00, 500.00), 2)
            elif category == "Travel":
                amount = round(random.uniform(200.00, 3000.00), 2)
            elif category == "Retail":
                amount = round(random.uniform(50.00, 500.00), 2)
            elif category == "Healthcare":
                amount = round(random.uniform(100.00, 1500.00), 2)
            elif category == "Subscriptions":
                amount = round(random.uniform(10.00, 100.00), 2)
            elif category == "Education":
                amount = round(random.uniform(100.00, 2500.00), 2)
            elif category == "Automobile":
                amount = round(random.uniform(200.00, 1000.00), 2)
            elif category == "Entertainment":
                amount = round(random.uniform(20.00, 300.00), 2)
            elif category == "Luxury Items":
                amount = round(random.uniform(100.00, 5000.00), 2)
            elif category == "Financial Services":
                amount = round(random.uniform(10.00, 200.00), 2)
    if random.random() < anomaly_chance:
        location = f"{fake.city()}, {fake.state_abbr()}" # Less than 2% chance to have a random location (fraud)
    else:
        location = find_typical_location(cursor, customer_id)  # Use the customer's common location
    card_type = random.choice(card_types)
    approval_status = random.choices(approval_statuses, weights, k=1)[0]
    payment_method = random.choice(payment_methods)
    is_fraud = "Undetermined"
    if approval_status == "Declined":
        note = random.choice(declined_notes)
    else:
        note = None 

    generated_charge = Charge(transaction_id, customer_id, timestamp, merchant_name, category, amount, location, 
                              card_type, approval_status, payment_method, is_fraud, note)
    
    return generated_charge

# Simulates a new charge being added to database, as if a payment was processed
def swipe_card():
    # Generate a new random charge
    newCharge = generate_charge(main_cursor)
    # Add charge to database with add_charge function
    add_charge(main_cursor, newCharge)
    return newCharge

# Takes in a charge and finds identical charges
def find_repeat_charges(cursor, charge):
    try:
        # Check if the transaction_id exists
        check_sql = "SELECT 1 FROM {table_name} WHERE transaction_id = %s".format(table_name=DATABASE_TABLE)
        cursor.execute(check_sql, (charge.transaction_id,))
        result = cursor.fetchone()

        if result:
            # SQL query to find repeat charges
            find_charges_sql = """
                            SELECT *
                            FROM {table_name}
                            WHERE customer_id = %s
                                AND timestamp = %s
                                AND location = %s
                            """.format(table_name=DATABASE_TABLE)
            # Execute the SQL Query
            cursor.execute(find_charges_sql, (charge.customer_id, charge.timestamp, charge.location,))
            duplicate_charges = cursor.fetchall()

            # Return duplicate charges for further analysis
            return duplicate_charges

        else:
            print(f"Transaction ID: {highlight("blue",charge.transaction_id)} is not in the database.")
            return []   
    
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
                        """.format(table_name=DATABASE_TABLE)
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
        # Query to calculate both average and standard deviation in one query
        avg_std_query_sql = """
                    SELECT AVG(amount) AS avg_amount, STDDEV_SAMP(amount) AS std_dev
                    FROM {table_name}
                    WHERE customer_id = %s
                    """.format(table_name=DATABASE_TABLE)
        # Execute the SQL Query
        cursor.execute(avg_std_query_sql, (customerID,))
        result = cursor.fetchone()

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

# Checks datetime of each charge for NULL or placeholder value and asks user to update value
def timestamp_check(cursor):
    try:
        # SQL query to find transactions with placeholder or NULL values
        find_null_timestamps = """
                                SELECT * 
                                FROM {table_name}
                                WHERE timestamp IS NULL OR timestamp = '1970-01-01'
                                """.format(table_name=DATABASE_TABLE)
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
                            """.format(table_name=DATABASE_TABLE)
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

# Helper function to check if a charge's category is within the expected bounds - returns False if not
def is_amount_valid(charge):
    category = charge.category
    amount = charge.amount

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
        "Other": 500.00  # Max value for unexpected categories
    }

    # Use "Other" as a fallback for any unexpected category
    max_allowed = category_bounds.get(category, category_bounds["Other"])
    
    # If amount is less than or equal to max_allowed, return True
    return amount <= max_allowed

# Function that takes a charge and determines fraudulence based on logic and defined rules
def flag_fraud(cursor, charge):
    try:
        reasons = []  # Collect fraud reasons here

        # Check if is_fraud is marked as Undetermined or NULL value
        if charge.is_fraud in ("Undetermined", None):

            # Check for various fraud conditions
            if charge.category == "Financial Services" and charge.amount > 1000.00:
                reasons.append(f"{highlight("blue",charge.category)} charge over $1000.00")

            if charge.amount > 3000.00 and charge.category not in ["Travel", "Luxury Items"]:
                reasons.append(f"${charge.amount} spent in Category: {highlight("blue",charge.category)}")

            avg_spent, std_dev = calculate_average_and_std_dev(cursor, charge.customer_id)
            if std_dev > 0:  # Avoid division by zero
                z_score = (charge.amount - avg_spent) / std_dev
                if abs(z_score) > 2.0:
                    reasons.append(f"Outlier in spending: Amount ${highlight("blue",charge.amount)}, Z-Score: {z_score:.2f}")

            duplicates = find_repeat_charges(cursor, charge)
            if len(duplicates) > 1:
                reasons.append(f"Duplicate charge. Found {highlight("blue",len(duplicates))} identical charges")

            typical_location = find_typical_location(cursor, charge.customer_id)
            if charge.location not in [typical_location, "Unknown"]:
                reasons.append(f"Location anomaly: {highlight("blue",charge.location)} (Expected: {typical_location})")

            if not is_amount_valid(charge):
                reasons.append(f"Charge Amount: ${charge.amount} out of bounds for Category: {highlight("blue",charge.category)}")

            # Set fraud status if any reasons were found
            if reasons:
                charge.set_fraud("FRAUD")
                update_transaction(main_connection, cursor, charge)
                print(f"Transaction ID: {highlight("blue",charge.transaction_id)} marked as {highlight("red",charge.is_fraud)} due to the following reasons:")
                for reason in reasons:
                    print(f"- {reason}")
                return True

            # If no fraud reasons, mark as Not Fraud
            charge.set_fraud("NOT FRAUD")
            print(f"Transaction ID: {highlight("blue",charge.transaction_id)} marked as {highlight("green",charge.is_fraud)} after analysis.")
            update_transaction(main_connection, cursor, charge)
            return False

        else:
            print(f"Transaction ID: {highlight("blue",charge.transaction_id)} is already set to {highlight("blue",charge.is_fraud)}")

    except Exception as e:
        print(f"Error processing transaction: {e}")
        cursor.rollback()
        return False  # Ensure no further processing
    
    
# Notifies customer of 'declined' charge status note
def notify_customer(cursor, charge):
    try:
        # SQL query to find declined charges for the given customer_id
        find_charge_sql = """
                          SELECT *
                          FROM {table_name}
                          WHERE approval_status = 'Declined' AND customer_id = %s
                          """.format(table_name=DATABASE_TABLE)
        # Execute the SQL query with customer_id
        cursor.execute(find_charge_sql, (DATABASE_TABLE,charge.customer_id,))
        declined_charges = cursor.fetchall()

        # If there are declined charges, print notifications for each
        for declined in declined_charges:
            transaction_id = declined[0]
            print(f"Transaction ID: {highlight("blue",transaction_id)} Declined. Transaction Note: {charge.note}")

    except Exception as e:
        print(f"Error retrieving declined charges for Customer ID: {highlight("blue",charge.customer_id)}: {e}")


# Close the connection to the PostgreSQL database
database_close(main_connection, main_cursor)