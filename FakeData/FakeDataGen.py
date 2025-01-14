import pandas as pd
import random
import uuid
from faker import Faker

# Initialize Faker instance for generating realistic data
fake = Faker()

# Define parameters for dataset creation
num_transactions = 75000  # Adjust this number to control the dataset size
categories = [
    "Groceries", "Dining", "Travel", "Retail", "Utilities", "Healthcare",
    "Subscriptions", "Education", "Automobile", "Entertainment", "Charity",
    "Insurance", "Miscellaneous", "Financial Services", "Luxury Items"
]
card_types = ["Visa", "Mastercard", "American Express", "Discover"]
approval_statuses = ["Approved", "Declined", "Pending"]
weights = [65, 20, 15]  # Corresponding to 65%, 20%, and 15%
payment_methods = ["Chip", "Swipe", "Contactless", "Online Payment", "Mobile Wallet"]

# Helper function to simulate normal or fraudulent patterns
def generate_transaction():
    transaction_id = str(uuid.uuid4())[:8]
    customer_id = str(uuid.uuid4())[:8]
    timestamp = fake.date_time_this_decade()
    merchant_name = fake.company()
    category = random.choice(categories)
    amount = round(random.uniform(1.0, 5000.0), 2)
    location = f"{fake.city()}, {fake.state_abbr()}"
    card_type = random.choice(card_types)
    approval_status = random.choices(approval_statuses, weights, k=1)[0]
    payment_method = random.choice(payment_methods)

    # Introduce anomalies to simulate potential fraud
    if random.random() < 0.02:  # ~2% chance of being fraudulent
        if random.random() < 0.5:
            amount = round(random.uniform(3000.0, 10000.0), 2)  # Unusually high amount
        if random.random() < 0.5:
            location = f"{fake.city()}, {fake.state_abbr()}"  # Distant/uncommon location
        if random.random() < 0.5:
            timestamp = fake.date_time_this_month()  # Rapid transactions in a short time frame

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
        "Payment Method": payment_method
    }

# Generate dataset
data = [generate_transaction() for _ in range(num_transactions)]

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
output_path = "credit_card_transactions.csv"  # Change the path if needed
df.to_csv(output_path, index=False)

print(f"Dataset saved to {output_path}")