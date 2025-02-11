# CARD GUARD
# Data Processing File

# Import libraries
from config import *
from models import *
from utils import *

# Import class functions
from transaction_functions import *
from customer_functions import *

# IMPLEMENT PYSPARK
from pyspark.sql import SparkSession


# Set database connection details
db_url = f"jdbc:postgresql://{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"
db_properties = {
    "user": DATABASE_CONFIG['user'],
    "password": DATABASE_CONFIG['password'],
    "driver": "org.postgresql.Driver"
}

# Initialize SparkSession with the JDBC driver on the local machine (No need for Hadoop implementation)
spark = SparkSession.builder \
    .appName("Card Guard") \
    .master("local[*]") \
    .config("spark.jars", "file:///C:/PostgreSQL/postgresql-42.7.5.jar") \
    .config("spark.driver.memory", "8g") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.maxResultSize", "4g") \
    .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC") \
    .config("spark.executor.heartbeatInterval", "60s") \
    .getOrCreate()

# Load data from PostgreSQL into Spark
df = spark.read.jdbc(url=db_url, table=TRANSACTIONS_TABLE, properties=db_properties)

# Reduce number of partitions
df = df.repartition(10)

# Show a preview of the data
df.limit(5).show()