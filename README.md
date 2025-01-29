# Card Guard - Fraud Detection Application

## Overview

Card Guard is a comprehensive fraud detection application designed to identify suspicious credit card transactions using advanced algorithms and rule-based logic. It integrates with PostgreSQL for efficient data management and supports real-time analysis of transaction data to enhance financial security.

## Features

- **Transaction Management**: 
  - Add, update, and delete transactions manually or programmatically.
  - Simulate new transactions using realistic data generation with the `Faker` library.

- **Fraud Detection**:
  - Rule-based and statistical anomaly detection, including:
    - Expenditure category bounds.
    - Locational anomalies.
    - Duplicate transactions.
    - Z-score-based outlier detection for spending patterns.
  - Dynamic fraud flagging with detailed explanations.

- **Data Analysis**:
  - Average and standard deviation of spending for individual customers.
  - Locational profiling to identify typical spending regions.

- **Integration with PostgreSQL**:
  - Efficient handling of large datasets using Apache Spark for parallelized processing.
  - Data loading and storage using SQLAlchemy.

- **Testing Framework**:
  - Unit tests for key functionalities using `pytest` and `unittest.mock`.

## Technologies Used

- **Backend**: Python
- **Database**: PostgreSQL
- **Data Processing**: Apache Spark, Pandas, SQLAlchemy
- **Libraries**: 
  - `psycopg2` for database connectivity.
  - `pytest` and `unittest.mock` for testing.
  - `Faker` for realistic transaction simulation.

## Project Structure

```plaintext
Fraud-Detection/
│
├── charge_functions.py          # Core transaction logic and fraud detection rules
├── data_processing.py           # Parallel data loading and analysis using Apache Spark
├── test_charge_functions.py     # Unit tests for key functionalities
├── config.py                    # Database configuration settings
├── README.md                    # Project documentation
```

## Setup

### Prerequisites
- Python 3.8 or higher
- PostgreSQL installed and configured

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tpetrow-portfolio/Fraud-Detection.git
   cd Fraud-Detection

2. **Configure the database**
   - Update the `DATABASE_CONFIG` in `confg.py` with your PostgreSQL credentials, and info

3. **Run the Application**
    ```bash
       python data_processing.py
    ```

## Usage

- **Simulate Transactions**:
     - Use `swipe_card()` to generate and insert realistic transactions into the database.
- **Flag Fraudulent Transactions**:
     - Call `flag_fraud(charge)` to analyze individual transactions for anomalies.
- **Analyze Data**:
     - Run `calculate_avg_spent(customer_id)` to determine customer spending habits.
     - Use `find_typical_location(customer_id)` to identify common transaction locations.
- **Run Tests**: 
  ```bash
     pytest test_charge_functions.py
