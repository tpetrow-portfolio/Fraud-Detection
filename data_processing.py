# CARD GUARD
# Data Processing File

# Import libraries
import numpy as np
import pandas as pd
import psycopg2
from config import DATABASE_CONFIG

# Import functions from charge_functions.py
from charge_functions import *

# Connect to PostgreSQL Database using the helper function
conn = database_connect(**DATABASE_CONFIG)
cur = conn.cursor()  # Cursor to execute SQL commands

# INSERT DATABASE HERE AND START ENGINEERING
# needs to go through all charges, would be time consuming, should chunk up data, maybe multithread with Dask
