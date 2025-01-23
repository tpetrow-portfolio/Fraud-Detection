# CARD GUARD
# Data Processing File

# Import libraries
import psycopg2
from config import DATABASE_CONFIG
import random
from datetime import datetime
import uuid
from faker import Faker

# Helper function that establishes a connection to the PostgreSQL database
def database_connect(dbname, user, password, host, port=5432):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise

# Define 'Charge' class with all attributes of a charge from the database
class Charge:
    # Initialize all attributes with empty values to detect and handle improper import from database
    def __init__(self, transaction_id="", customer_id="", timestamp=None, merchant_name="", 
                category="", amount=0.00, location="", card_type="", approval_status="", payment_method="", is_fraud="Undetermined"):

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

# Updates the table with new transaction information when modified
def update_transaction(charge):
    try:
        # Connect to PostgreSQL Database using the helper function
        conn = database_connect(**DATABASE_CONFIG)
        cur = conn.cursor()  # Cursor to execute SQL commands
        
        # SQL query to update row with new transaction information
        update_table_sql = """
                UPDATE transactions
                SET customer_id = %s, timestamp = %s, merchant_name = %s, category = %s, amount = %s, 
                    location = %s, card_type = %s, approval_status = %s, payment_method = %s, is_fraud = %s
                WHERE transaction_id = %s
                """
        # Execute the SQL Query
        cur.execute(update_table_sql, (
            charge.customer_id, charge.timestamp, charge.merchant_name, charge.category, charge.amount,
            charge.location, charge.card_type, charge.approval_status, charge.payment_method, charge.is_fraud,
            charge.transaction_id,
        ))
        
        # Commit changes and close connections
        conn.commit()
        print(f"Transaction ID {charge.transaction_id} successfully updated.")
    except Exception as e:
        print(f"Error updating transaction {charge.transaction_id}: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Finds a customer's most common spending location for detecting locational anomaly fraud
def find_typical_location(customerID):
    # Connect to PostgreSQL Database using the helper function
    conn = database_connect(**DATABASE_CONFIG)
    cur = conn.cursor()
    try:
        # Query to find the most common location for the customer
        location_query_sql = """
            SELECT location, COUNT(*) AS frequency
            FROM transactions
            WHERE customer_id = %s
            GROUP BY location
            ORDER BY frequency DESC
            LIMIT 1;
        """
        # Execute the SQL Query
        cur.execute(location_query_sql, (customerID,))
        result = cur.fetchone()

        # Return the most common location or 'Unknown' if no result is found
        if result:
            return result[0]  # The most common location
        else:
            return "Unknown"
    
    except Exception as e:
        print(f"Error finding typical location for customer_id {customerID}: {e}")
        return "Unknown"
    
    finally:
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
    weights = [75, 10, 15]  # Corresponding to 75%, 10%, and 15%
    # Define list of payment methods
    payment_methods = ["Chip", "Swipe", "Contactless", "Online Payment", "Mobile Wallet"]
    uuid_list = [str(uuid.uuid4())[:8] for _ in range(4000)] # list of 4000 customer_id's

    # Probability of anomaly (used for location and amount)
    anomaly_chance = 0.02  # 2%

    # Generate simulated charge information
    transaction_id = str(uuid.uuid4()).replace('-', '')[:10]
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
        location = find_typical_location(customer_id)  # Use the customer's common location
    card_type = random.choice(card_types)
    approval_status = random.choices(approval_statuses, weights, k=1)[0]
    payment_method = random.choice(payment_methods)
    is_fraud = "Undetermined"

    generated_charge = Charge(transaction_id, customer_id, timestamp, merchant_name, category, amount, location, 
                              card_type, approval_status, payment_method, is_fraud)
    
    return generated_charge

# Adds a charge to database, allows for manual charge entry
def add_charge(charge):
    try:
        # Connect to PostgreSQL Database using the helper function
        conn = database_connect(**DATABASE_CONFIG)
        cur = conn.cursor()  # Cursor to execute SQL commands

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
                charge.payment_method, charge.is_fraud,
            ))
            # Commit the addition
            conn.commit()
            print(f"Transaction ID: {charge.transaction_id} successfully added to database!")

    except Exception as e:
        print("Failed to insert record into table:", e)
        if conn:
            conn.rollback()  # Roll back the transaction in case of an error

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()
    
# Removes a charge from database, allows for manual charge deletion via provided transactionID
def delete_charge(transactionID):
    # Connect to PostgreSQL Database using the helper function
    conn = database_connect(**DATABASE_CONFIG)
    cur = conn.cursor()  # Cursor to execute SQL commands
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
    # Connect to PostgreSQL Database using the helper function
    conn = database_connect(**DATABASE_CONFIG)
    cur = conn.cursor()  # Cursor to execute SQL commands
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
                                AND timestamp = %s
                                AND location = %s
                            """
            # Execute the SQL Query
            cur.execute(find_charges_sql, (charge.customer_id, charge.timestamp, charge.location,))
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

# Calculates the average amount of money spent by customer
def calculate_avg_spent(customerID):
    # Connect to PostgreSQL Database using the helper function
    conn = database_connect(**DATABASE_CONFIG)
    cur = conn.cursor()  # Cursor to execute SQL commands
    try:
        # Query to calculate the average spending amount
        avg_query_sql = """
                        SELECT AVG(amount) AS avg_amount
                        FROM transactions
                        WHERE customer_id = %s
                        """
        # Execute the SQL Query
        cur.execute(avg_query_sql, (customerID,))
        result = cur.fetchone()

        # Extract the average amount, handling NULL results from the query
        avg_amount = result[0] if result[0] is not None else 0.0
        return avg_amount

    except Exception as e:
        print(f"Error calculating average for customer_id {customerID}: {e}")
        return 0.0

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# Takes in a customer_id and finds the average amount of money spent by customer to help with Z-Score
def calculate_average_and_std_dev(customerID):
    # Connect to PostgreSQL Database using the helper function
    conn = database_connect(**DATABASE_CONFIG)
    cur = conn.cursor()  # Cursor to execute SQL commands
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

# Checks datetime of each charge for NULL or placeholder value and asks user to update value
def timestamp_check():
    # Connect to PostgreSQL Database using the helper function
    conn = database_connect(**DATABASE_CONFIG)
    cur = conn.cursor()  # Cursor to execute SQL commands
    try:
        # SQL query to find transactions with placeholder or NULL values
        find_null_timestamps = """
                                SELECT * 
                                FROM transactions 
                                WHERE timestamp IS NULL OR timestamp = '1970-01-01'
                                """
        # Execute the SQL Query
        cur.execute(find_null_timestamps)
        missing_timestamps = cur.fetchall()

        # If there are missing timestamps, prompt user to update
        if missing_timestamps:
            print(f"Transactions found with NULL or placeholder timestamps.")
            for transaction in missing_timestamps:
                transaction_id = transaction[0]
                print(f"Transaction ID {transaction_id} has a missing timestamp.")
                user_input = input(f"Please enter a valid timestamp for Transaction ID {transaction_id}: ")
                if user_input:
                    try:
                        new_timestamp = datetime.strptime(user_input, '%Y-%m-%d %H:%M:%S')
                        # Update the transaction's timestamp in the database
                        update_sql = """
                            UPDATE transactions
                            SET timestamp = %s
                            WHERE transaction_id = %s
                            """
                        # Execute the SQL Query
                        cur.execute(update_sql, (new_timestamp, transaction_id,))

                        # Commit the transaction
                        conn.commit()
                        print(f"Transaction ID {transaction_id} updated successfully.")
                    except ValueError:
                        print("Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'.")
                else:
                    print(f"No input received for Transaction ID {transaction_id}. Skipping update.")

        else:
            print("No transactions found with missing timestamps.")
                    
    except Exception as e:
        print(f"Error updating transactions: {e}")
        conn.rollback()  # Roll back in case of an error

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# Helper function to check if a charge's category is within the expected bounds - returns False if not
def is_amount_valid(charge):
    category = charge.category
    amount = charge.amount

    # Category bounds for each category (only considering the max value)
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
        "Financial Services": 200.00
    }
    
    # Check if the amount exceeds the max allowed value
    if amount > category_bounds[category]:
        return False
    
    return True

# Function that takes a charge and determines fraudulence based on logic and defined rules
def flag_fraud(charge):
    try:
        # Check if is_fraud is marked as Undetermined or NULL value
        if charge.is_fraud in ("Undetermined", None):
            # Flag any charge categorized as 'Financial Services' over $1000
            if charge.category == "Financial Services" and charge.amount > 1000.00:
                charge.set_fraud("Fraud")
                print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to {charge.category} charge over $1000.00")
                update_transaction(charge)
                # Return True to indicate that fraud was detected
                return True

            # Flag any charge above 3000 that is not categorized as 'Travel' or 'Luxury Items'
            if charge.amount > 3000.00 and charge.category not in ["Travel", "Luxury Items"]:
                charge.set_fraud("Fraud")
                print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to [${charge.amount} spent in Category: {charge.category}]")
                update_transaction(charge)
                # Return True to indicate that fraud was detected
                return True

            # Calculate Z-Score
            avg_spent, std_dev = calculate_average_and_std_dev(charge.customer_id)
            if std_dev > 0:  # Avoid division by zero
                z_score = (charge.amount - avg_spent) / std_dev
                # Flag outliers in customer spending (Z-Score > 2)
                if abs(z_score) > 2.0:
                    charge.set_fraud("Fraud")
                    print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to outlier in spending."
                            f"Charge Amount: ${charge.amount}, Z-Score: {z_score:.2f}")
                    update_transaction(charge)
                    # Return True to indicate that fraud was detected
                    return True

            # Check for identical charges occur with same customer_id, location, and timestamp
            duplicates = find_repeat_charges(charge)
            if len(duplicates) > 1:  # More than one charge with the same attributes
                charge.set_fraud("Fraud")
                print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to duplicate charge. Analysis found {len(duplicates)} identical charges.")
                update_transaction(charge)
                # Return True to indicate that fraud was detected
                return True
            
            # Check for locational anomalies
            typical_location = find_typical_location(charge.customer_id)
            if charge.location not in [typical_location, "Unknown"]:
                charge.set_fraud("Fraud")
                print(
                        f"Transaction ID: {charge.transaction_id} marked as FRAUD due to location anomaly. "
                        f"Location: {charge.location} does not match typical location: {typical_location}"
                    )
                update_transaction(charge)
                # Return True to indicate that fraud was detected
                return True
            
            # Check if a charge's category is within the expected expenditure amount bounds
            if not is_amount_valid(charge):
                charge.set_fraud("Fraud")
                print(f"Transaction ID: {charge.transaction_id} marked as FRAUD due to Charge Amount: {charge.amount} out of expected bound for Category: {charge.category}")
                update_transaction(charge)
                # Return True to indicate that fraud was detected
                return True

            # If none of the above conditions are met, mark as Not Fraud
            charge.set_fraud("Not Fraud")
            print(f"Transaction ID: {charge.transaction_id} marked as NOT FRAUD after analysis.")
            update_transaction(charge)
            # Return False to indicate that fraud was not detected
            return False
        
        # If is_fraud is already updated
        else:
            print(f"Transaction ID: {charge.transaction_id} is already set to {charge.is_fraud}")

    except Exception as e:
        print(f"Error processing transaction {charge.transaction_id}: {e}")
        return False
    
