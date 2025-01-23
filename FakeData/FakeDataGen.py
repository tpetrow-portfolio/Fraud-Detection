import pandas as pd
import random
import uuid
from faker import Faker

# Initialize Faker instance for generating realistic data
fake = Faker()

# Maintain a dictionary to map customer_id to their default location
customer_locations = {}

# Probability of anomaly (used for location and amount)
anomaly_chance = 0.02  # 2%


# Define parameters for dataset creation
num_transactions = 10000000 # Adjust this number to control the dataset size
categories = [
    "Groceries", "Dining", "Travel", "Retail", "Utilities", "Healthcare",
    "Subscriptions", "Education", "Automobile", "Entertainment", "Charity",
    "Insurance", "Miscellaneous", "Financial Services", "Luxury Items"
]
card_types = ["Visa", "Mastercard", "American Express", "Discover"]
approval_statuses = ["Approved", "Declined", "Pending"]
weights = [75, 10, 15]  # Corresponding to 75%, 10%, and 15%
payment_methods = ["Chip", "Swipe", "Contactless", "Online Payment", "Mobile Wallet"]

uuid_list = [str(uuid.uuid4())[:8] for _ in range(4000)] # list of 4000 customer_id's

last_charge = []

# Helper function to simulate normal or fraudulent patterns
def generate_transaction():
    global last_charge, customer_locations
        
    transaction_id = str(uuid.uuid4()).replace('-', '')[:10]
    customer_id = random.choice(uuid_list)
    timestamp = fake.date_time_this_decade().strftime('%Y-%m-%d %H:%M:%S')
    merchant_name = fake.company()
    category = random.choice(categories)
    if category in ["Groceries", "Utilities", "Charity", "Insurance", "Miscellaneous"]:
        # 2% chance to generate an anomalous value for lower expense categories
        if random.random() < anomaly_chance:
            amount = round(random.uniform(1.0, 5000.0), 2)  # Anomalous range
        else:
            amount = round(random.uniform(10.00, 300.00), 2)  # Normal range
    elif category in ["Dining", "Travel", "Retail", "Healthcare", "Subscriptions", "Education", 
                  "Automobile", "Entertainment", "Luxury Items", "Financial Services"]:
        # 2% chance to generate an anomalous value for higher expense categories
        if random.random() < anomaly_chance:
            amount = round(random.uniform(1.0, 10000.0), 2)  # Anomalous range
        else:
            if category == "Dining":
                amount = round(random.uniform(50.00, 500.00), 2) # Normal range
            elif category == "Travel":
                amount = round(random.uniform(200.00, 3000.00), 2) # Normal range
            elif category == "Retail":
                amount = round(random.uniform(50.00, 500.00), 2) # Normal range
            elif category == "Healthcare":
                amount = round(random.uniform(100.00, 1500.00), 2) # Normal range
            elif category == "Subscriptions":
                amount = round(random.uniform(10.00, 100.00), 2) # Normal range
            elif category == "Education":
                amount = round(random.uniform(100.00, 2500.00), 2) # Normal range
            elif category == "Automobile":
                amount = round(random.uniform(200.00, 1000.00), 2) # Normal range
            elif category == "Entertainment":
                amount = round(random.uniform(20.00, 300.00), 2) # Normal range
            elif category == "Luxury Items":
                amount = round(random.uniform(100.00, 5000.00), 2) # Normal range
            elif category == "Financial Services":
                amount = round(random.uniform(10.00, 200.00), 2) # Normal range
    # Determine the location
    if customer_id not in customer_locations:
        # Generate a new location for locational anomaly or first-time customer
        location = f"{fake.city()}, {fake.state_abbr()}"
        customer_locations[customer_id] = location
    elif  random.random() < anomaly_chance:
        location = f"{fake.city()}, {fake.state_abbr()}" # Less than 2% chance to have a random location (fraud)
    else:
        location = customer_locations[customer_id]  # Use the customer's common location
    card_type = random.choice(card_types)
    approval_status = random.choices(approval_statuses, weights, k=1)[0]
    payment_method = random.choice(payment_methods)
    is_fraud = "Undetermined"

    # Introduce anomalies to simulate potential fraud
    if random.random() < 0.03:  # ~3% chance of being fraudulent
        if random.random() < 0.3:
            amount = round(random.uniform(3000.0, 10000.0), 2)  # Unusually high amount
        if random.random() < 0.3:
            location = f"{fake.city()}, {fake.state_abbr()}"  # Distant/uncommon location
        if random.random() < 0.3:
            # Use the last charge for anomalies
            if last_charge:  # Only use the last charge if it exists
                transaction_id = str(uuid.uuid4()).replace('-', '')[:10]
                customer_id = last_charge[1]
                timestamp = last_charge[2]
                merchant_name = last_charge[3]
                category = last_charge[4]
                if category in ["Groceries", "Utilities", "Charity", "Insurance", "Miscellaneous"]:
                    # 2% chance to generate an anomalous value for lower expense categories
                    if random.random() < anomaly_chance:
                        amount = round(random.uniform(1.0, 5000.0), 2)  # Anomalous range
                    else:
                        amount = round(random.uniform(10.00, 300.00), 2)  # Normal range
                elif category in ["Dining", "Travel", "Retail", "Healthcare", "Subscriptions", "Education", 
                            "Automobile", "Entertainment", "Luxury Items", "Financial Services"]:
                    # 2% chance to generate an anomalous value for higher expense categories
                    if random.random() < anomaly_chance:
                        amount = round(random.uniform(1.0, 10000.0), 2)  # Anomalous range
                    else:
                        if category == "Dining":
                            amount = round(random.uniform(50.00, 500.00), 2)
                        elif category == "Travel":
                            amount = round(random.uniform(200.00, 3000.00), 2)
                        elif category == "Retail":
                            amount = round(random.uniform(50.00, 500.00), 2)
                        elif category == "Healthcare":
                            amount = round(random.uniform(100.00, 1500.00), 2)
                        elif category == "Subscriptions":
                            amount = round(random.uniform(10.00, 100.00), 2)
                        elif category == "Education":
                            amount = round(random.uniform(100.00, 2500.00), 2)
                        elif category == "Automobile":
                            amount = round(random.uniform(200.00, 1000.00), 2)
                        elif category == "Entertainment":
                            amount = round(random.uniform(20.00, 300.00), 2)
                        elif category == "Luxury Items":
                            amount = round(random.uniform(100.00, 5000.00), 2)
                        elif category == "Financial Services":
                            amount = round(random.uniform(10.00, 200.00), 2)
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