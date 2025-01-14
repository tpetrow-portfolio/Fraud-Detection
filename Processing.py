# CARD GUARD

# Data Processing File

# Import Libraries
import psycopg2
import numpy as np
import pandas as pd

# Connect to PostgreSQL Database
conn = psycopg2.connect(dbname="Credit Card Transactions", user="postgres", password="password123", host="localhost")
cur = conn.cursor() # Cursor that allows execution of SQL commands


# Function that takes a charge and determines fraudulence based on logic statements
# needs to go through all charges, would be time consuming, should chunk up data
def is_fraud(charge):
    # if charge is > $3000
        # if charge is not Travel, Luxury Items where $3000 is more tolerated

    # if charges occur rapidly with same customer_id

    # if charges occur in a varying location
    return True


# Close Connection with database
cur.close()
cur.close()