# CARD GUARD
# Customer Functions

# Import libraries
from config import *
from models import *
from utils import *
import random
import uuid
from faker import Faker

# Connect to PostgreSQL Database using the helper function
main_connection = database_connect(**DATABASE_CONFIG)  # Database connection passed into functions
main_cursor = main_connection.cursor()  # Cursor to execute SQL commands passed into functions

# Stores all transactions for a given customer_id in a list
def list_of_transactions(cursor, customerID):
    try:
        # Check if the customer exists in customers table
        check_sql = "SELECT * FROM {table_name} WHERE customer_id = %s".format(table_name=CUSTOMERS_TABLE)
        cursor.execute(check_sql, (customerID,))
        
        # Use fetchone to get a single result
        result = cursor.fetchone()

        # If customer exists, find and return a list of their transactions from the transactions table
        if result:
            get_transactions_sql = "SELECT transaction_id FROM {table_name} WHERE customer_id = %s".format(table_name=TRANSACTIONS_TABLE)
            cursor.execute(get_transactions_sql, (customerID,))
            transactions_list = cursor.fetchall()
            if transactions_list: return transactions_list
            else: 
                print(f"Customer ID: {highlight("blue",customerID)} does not have any transactions")
                return []
        # If customer does not exist, return an empty list
        else:
            print(f"Customer ID: {highlight("blue",customerID)} is not in the database.")
            return []
        
    except Exception as e:
        print(f"Error finding customer: {e}")
        raise  # Re-raise the exception for better error propagation

# Lists all of the transactions marked as fraud for a given customer_id
def list_fraud(cursor, customerID):
    

# Helper function to find a customer_id in database from customer ID
def find_customer(cursor, customerID):
    try:
        # Check if the customer_id exists
        check_sql = "SELECT * FROM {table_name} WHERE customer_id = %s".format(table_name=CUSTOMERS_TABLE)
        cursor.execute(check_sql, (customerID,))
        
        # Use fetchone to get a single result
        result = cursor.fetchone()

        # Return the result if found, otherwise return None
        if result:
            # Create a Customer object from the tuple result
            return Customer(*result)  # Unpacks the result tuple into the Customer constructor
        else:
            print(f"Customer ID: {highlight("blue",customerID)} is not in the database.")
            return None

    except Exception as e:
        print(f"Error finding customer: {e}")
        raise  # Re-raise the exception for better error propagation

# Adds a customer to database, allows for manual customer entry
def add_customer(cursor, customer):
    try:
        # Check if the customer_id already exists
        check_sql = "SELECT 1 FROM {table_name} WHERE customer_id = %s".format(table_name=CUSTOMERS_TABLE)
        cursor.execute(check_sql, (customer.customer_id,))
        result = cursor.fetchone()

        if result:
            print(f"Customer ID: {highlight('blue', customer.customer_id)} already exists in the database. Skipping insertion.")
        else:
            # SQL to insert new customer
            insert_sql = """
                INSERT INTO {table_name} (
                    customer_id, first_name, last_name, age, location, phone_number
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """.format(table_name=CUSTOMERS_TABLE)
            # Execute the SQL Query
            cursor.execute(insert_sql, (
                customer.customer_id, customer.first_name, customer.last_name, 
                customer.age, customer.location, customer.phone_number
            ))
            # Commit the addition
            main_connection.commit()
            print(f"Customer ID: {highlight('blue', customer.customer_id)} ({highlight('blue', customer.last_name)}, {highlight('blue', customer.first_name)}) successfully added to database!")

    except Exception as e:
        print("Failed to insert customer into table:", e)
        main_connection.rollback()  # Roll back the query in case of an error

# Removes a customer from database, allows for manual customer deletion via provided customerID
def delete_customer(cursor, customer):    
    try:
        # Check if the customer_id exists
        check_sql = "SELECT 1 FROM {table_name} WHERE customer_id = %s".format(table_name=CUSTOMERS_TABLE)
        cursor.execute(check_sql, (customer.customer_id,))
        result = cursor.fetchone()

        if result:
            # SQL FUNCTION to delete a customer by customer_id
            remove_sql = "DELETE FROM {table_name} WHERE customer_id = %s".format(table_name=CUSTOMERS_TABLE)
            # Execute the SQL Query
            cursor.execute(remove_sql, (customer.customer_id,))
        
            # Commit the deletion
            main_connection.commit()
            print(f"Customer ID: {highlight('blue', customer.customer_id)} ({highlight('blue', customer.last_name)}, {highlight('blue', customer.first_name)}) successfully removed from database!")

        else:
            print(f"Customer ID: {highlight("blue",customer.customer_id)} is not in the database.")
    
    except Exception as e:
        print(f"Failed to delete customer from table: {e}")
        main_connection.rollback()  # Roll back the query in case of an error

# Function to generate a randomized customer - returns a Customer
def generate_customer(cursor):
    # Initialize Faker instance for generating realistic data
    fake = Faker()

    # Helper function to generate a unique customer ID
    def generate_unique_customer_id():
        try:
            while True:
                # Generate a new customer ID
                customer_id = str(uuid.uuid4())[:10].replace('-', '')

                # Check if the customer ID exists
                check_sql = "SELECT 1 FROM {table_name} WHERE customer_id = %s".format(table_name=CUSTOMERS_TABLE)
                cursor.execute(check_sql, (customer_id,))
                result = cursor.fetchone()

                if not result:  # If no match found
                    return customer_id  # Unique ID found, return it

        except Exception as e:
            print(f"Error generating customer ID: {e}")
            raise

    # Generate simulated customer
    customer_id = generate_unique_customer_id()
    first_name = fake.first_name()
    last_name = fake.last_name()
    age = random.randint(18, 85)  # Age range from 18 to 85
    location = f"{fake.city()}, {fake.state_abbr()}"
    phone_number = fake.bothify('###-###-####')
    
    generated_customer = Customer(customer_id, first_name, last_name, age, location, phone_number)
    
    return generated_customer

# Updates the table with new customer information when modified
def update_customer(cursor, customer):
    try:        
        # SQL query to update row with new customer information
        update_table_sql = """
                UPDATE {table_name}
                SET first_name = %s, last_name = %s, age = %s, location = %s, phone_number = %s
                WHERE customer_id = %s
                """.format(table_name=CUSTOMERS_TABLE)
        # Execute the SQL Query
        cursor.execute(update_table_sql, (customer.first_name, customer.last_name, 
                customer.age, customer.location, customer.phone_number, 
                customer.customer_id,
        ))
        
        # Commit changes and close connections
        main_connection.commit()
        print(f"Customer ID: {highlight("blue",customer.customer_id)} successfully updated.")
    except Exception as e:
        print(f"Error updating Customer ID:  {highlight("blue",customer.customer_id)}: {e}")


# Close the connection to the PostgreSQL database
database_close(main_connection, main_cursor)