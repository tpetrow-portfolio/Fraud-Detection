import pandas as pd
import random
import uuid
from faker import Faker

# Initialize Faker instance for generating realistic data
fake = Faker()

# Define parameters for dataset creation
num_transactions = 100000  # Adjust this number to control the dataset size
categories = [
    "Groceries", "Dining", "Travel", "Retail", "Utilities", "Healthcare",
    "Subscriptions", "Education", "Automobile", "Entertainment", "Charity",
    "Insurance", "Miscellaneous", "Financial Services", "Luxury Items"
]
card_types = ["Visa", "Mastercard", "American Express", "Discover"]
approval_statuses = ["Approved", "Declined", "Pending"]
weights = [65, 20, 15]  # Corresponding to 65%, 20%, and 15%
payment_methods = ["Chip", "Swipe", "Contactless", "Online Payment", "Mobile Wallet"]

uuid_list = [str(uuid.uuid4())[:8] for _ in range(5000)] # list of 5000 customer_id's

last_charge = []
# Helper function to simulate normal or fraudulent patterns
def generate_transaction():
    global last_charge
        
    transaction_id = str(uuid.uuid4())[:8]
    customer_id = random.choice(uuid_list)
    timestamp = fake.date_time_this_decade()
    merchant_name = fake.company()
    category = random.choice(categories)
    amount = round(random.uniform(1.0, 5000.0), 2)
    location = f"{fake.city()}, {fake.state_abbr()}"
    card_type = random.choice(card_types)
    approval_status = random.choices(approval_statuses, weights, k=1)[0]
    payment_method = random.choice(payment_methods)
    is_fraud = "Undetermined"

    # Introduce anomalies to simulate potential fraud
    if random.random() < 0.03:  # ~3% chance of being fraudulent
        if random.random() < 0.5:
            amount = round(random.uniform(3000.0, 10000.0), 2)  # Unusually high amount
        if random.random() < 0.5:
            location = f"{fake.city()}, {fake.state_abbr()}"  # Distant/uncommon location
        if random.random() < 0.5:
            # Use the last charge for anomalies
            if last_charge:  # Only use the last charge if it exists
                transaction_id = str(uuid.uuid4())[:8]
                customer_id = last_charge[1]
                timestamp = last_charge[2]
                merchant_name = last_charge[3]
                category = last_charge[4]
                amount = round(random.uniform(1.0, 5000.0), 2)  # Reset amount
                location = last_charge[6]
                card_type = last_charge[7]
                approval_status = last_charge[8]
                payment_method = last_charge[9]
    
    # Update last_charge with the most recent transaction data
    last_charge = [transaction_id, customer_id, timestamp, merchant_name, category, amount, location, card_type, approval_status, payment_method, is_fraud]


    return {
        "Transaction ID": transaction_id,
        "Customer ID": customer_id,
        "Timestamp": timestamp,
        "Merchant Name": merchant_name,
        "Category": category,
        "Amount": amount,
        "Location": location,
        "Card Type": card_type,
        "Approval Status": approval_status,
        "Payment Method": payment_method,
        "Is Fraud": is_fraud
    }

# Generate dataset
data = [generate_transaction() for _ in range(num_transactions)]

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
output_path = "credit_card_transactions.csv"  # Change the path if needed
df.to_csv(output_path, index=False)

print(f"Dataset saved to {output_path}")