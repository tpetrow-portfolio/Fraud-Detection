# CARD GUARD
# utils.py houses general utility functions to assist other files

import csv
import psycopg2

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

# Function for chunking large datasets for batch processing
def chunk_data(data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

# Function for writing a data result to CSV file
def write_to_csv(data, filename="output.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)