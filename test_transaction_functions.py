# CARD GUARD
# charge_functions.py Testing File

from unittest.mock import patch, MagicMock
from datetime import datetime
from transaction_functions import *
import pytest

@pytest.fixture
def sample_charge():
    # Create a sample Charge object for testing
    return Charge(
        transaction_id="TestTransaction",
        customer_id="TestCustomer",
        timestamp=None,
        merchant_name="Example Merchant",
        category="Electronics",
        amount=150.75,
        location="New York",
        card_type="Credit",
        approval_status="Approved",
        payment_method="Online",
        is_fraud="Undetermined"
    )

@patch("processing.psycopg2.connect")  # Mock the database connection
# Test Update Transaction Function
def test_update_transaction(mock_connect, sample_charge):
    # Create a mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulate a successful update
    mock_cursor.rowcount = 1

    # Call the function
    update_transaction(sample_charge)

    # Verify the SQL execution
    mock_cursor.execute.assert_called_once_with(
        """
                UPDATE transactions
                SET customer_id = %s, timestamp = %s, merchant_name = %s, category = %s, amount = %s, 
                location = %s, card_type = %s, approval_status = %s, payment_method = %s, is_fraud = %s
                WHERE transaction_id = %s
        """,
        (
            sample_charge.customer_id, sample_charge.timestamp, sample_charge.merchant_name,
            sample_charge.category, sample_charge.amount, sample_charge.location,
            sample_charge.card_type, sample_charge.approval_status, sample_charge.payment_method,
            sample_charge.is_fraud, sample_charge.transaction_id
        )
    )

    # Verify that commit was called
    mock_conn.commit.assert_called_once()

    # Verify the connection and cursor were closed
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

# Test that generated charges are valid
def test_generate_charge():
    # Generate a charge
    charge = generate_charge()

    # Check the type of the returned object
    assert isinstance(charge, Charge), "The returned object is not an instance of Charge."

    # Validate individual attributes
    assert len(charge.transaction_id) == 8, "Transaction ID is not 8 characters long."
    assert isinstance(charge.customer_id, str) and len(charge.customer_id) == 8, "Customer ID is not valid."
    assert isinstance(charge.timestamp, datetime), "Timestamp is not a datetime."
    assert isinstance(charge.merchant_name, str), "Merchant name is not a string."
    assert isinstance(charge.category, str), "Category is not a string."
    assert 1.0 <= charge.amount <= 5000.0, "Amount is out of range."
    assert isinstance(charge.location, str), "Location is not a string."
    assert charge.card_type in ["Visa", "Mastercard", "American Express", "Discover"], "Card type is invalid."
    assert charge.approval_status in ["Approved", "Declined", "Pending"], "Approval status is invalid."
    assert charge.payment_method in ["Chip", "Swipe", "Contactless", "Online Payment", "Mobile Wallet"], "Payment method is invalid."
    assert charge.is_fraud == "Undetermined", "Default fraud status is not 'Undetermined'."

def test_randomization():
    # Generate two charges and ensure they are different
    charge1 = generate_charge()
    charge2 = generate_charge()

    assert charge1.transaction_id != charge2.transaction_id, "Transaction IDs are not unique."
    assert charge1.customer_id != charge2.customer_id or charge1.timestamp != charge2.timestamp, \
        "Generated charges are too similar and may lack randomization."





testCharge = Charge("TestTransaction", "TestCustomer", None, "Test Store", "Test Category", 
                        100.00, "America", "MasterCard","Approved","Online")
testCharge2 = Charge("TestTransaction2", "TestCustomer", None, "Test Store", "Test Category", 
                        100.00, "America", "MasterCard","Approved","Online")
#add_charge(testCharge)
#add_charge(testCharge2)
#flag_fraud(testCharge) # Should flag as Not Fraud
#flag_fraud(testCharge2) # Should flag as Fraud
#delete_charge("TestTransaction")
#delete_charge("TestTransaction2")'''
#timestamp_check()

## TESTING

'''
# Test outer conditional - If transaction amount is 0 or negative
testTransaction = swipe_card()
testTransaction.amount = 0
flag_fraud(main_cursor, testTransaction)
delete_transaction(main_cursor, testTransaction.transaction_id)
'''

'''
# Test nested conditional - If is_fraud is already set
testTransaction = swipe_card()
testTransaction.is_fraud = "FRAUD"
flag_fraud(main_cursor, testTransaction)
delete_transaction(main_cursor, testTransaction.transaction_id)
'''

'''
# Test second nested conditional - If approval_status is Declined
testTransaction = swipe_card()
testTransaction.approval_status = "Declined"
testTransaction.note = "Invalid Card Number"
flag_fraud(main_cursor, testTransaction)
delete_transaction(main_cursor, testTransaction.transaction_id)
'''

'''
# Test first fraud flagger - If transaction amount is outside of max bound for the transaction's category
testTransaction = swipe_card()
testTransaction.category = "Groceries"
testTransaction.amount = 700.00
flag_fraud(main_cursor, testTransaction)
delete_transaction(main_cursor, testTransaction.transaction_id)
'''

'''
# Test second fraud flagger - If the transaction amount is outside of the normal standard deviation, based on Z-Score calculation
testTransaction = swipe_card()
testTransaction.category = "Luxury Items"
testTransaction.amount = 4999.99
flag_fraud(main_cursor, testTransaction)
delete_transaction(main_cursor, testTransaction.transaction_id)
'''

'''
# Test third fraud flagger - If the transaction is identical to another transaction
testTransaction = swipe_card()
testTransaction2 = swipe_card()
testTransaction3 = swipe_card()
flag_fraud(main_cursor, testTransaction)
testTransaction2.customer_id = testTransaction.customer_id
testTransaction2.location = testTransaction.location
testTransaction2.merchant_name = testTransaction.merchant_name
testTransaction2.card_type = testTransaction.card_type
flag_fraud(main_cursor, testTransaction2)
testTransaction3.customer_id = testTransaction.customer_id
testTransaction3.location = testTransaction.location
testTransaction3.merchant_name = testTransaction.merchant_name
testTransaction3.card_type = testTransaction.card_type
flag_fraud(main_cursor, testTransaction3)
delete_transaction(main_cursor, testTransaction.transaction_id)
delete_transaction(main_cursor, testTransaction2.transaction_id)
delete_transaction(main_cursor, testTransaction3.transaction_id)
'''

'''
# Test fourth fraud flagger - If the transaction is outside the customer's typical location
testTransaction = swipe_card()
testTransaction.location = "Great Britain"
flag_fraud(main_cursor, testTransaction)
delete_transaction(main_cursor, testTransaction.transaction_id)
'''

'''
# Test fifth fraud flagger - If the transaction has an unexpected category for customer's age
testTransaction = swipe_card()
testTransaction.customer_id = "951cfea37" # A 19 year old customer
testTransaction.category = "Bar Service"
flag_fraud(main_cursor, testTransaction)
delete_transaction(main_cursor, testTransaction.transaction_id)
'''