# CARD GUARD
# Data Processing File

# Import libraries
from config import DATABASE_CONFIG
from dask import delayed, compute
import pandas as pd
import dask.dataframe as dd

# Import functions from charge_functions.py
from charge_functions import *

# Extract credentials from DATABASE_CONFIG and place in string for Dask connection
db_config = DATABASE_CONFIG
conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

# Function to load data into Dask
def load_data():
    
    # Fetch data using pandas
    df_pandas = pd.read_sql("SELECT * FROM transactions", conn_str)
    
    # Convert the pandas DataFrame to a Dask DataFrame
    df_dask = dd.from_pandas(df_pandas, npartitions=4)
    
    return df_dask

# Load data
df = load_data()

# Dataframe grouped by customer_id
grouped_df = df.groupby('customer_id')

# 
customer_transactions_df = grouped_df.compute()

# View the first 10 rows of the Dask DataFrame
df.head(10)