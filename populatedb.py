import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient
from faker import Faker
import random

# Setup Faker and MongoDB connection
fake = Faker()
client = MongoClient("mongodb+srv://USERNAME:PASSWORD@cluster0.cw6ev.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["payments"]  # Replace with your database name
debit_collection = db["debit_transaction"]
credit_collection = db["credit_transaction"]

# Function to generate a random transaction document
def generate_debit_transaction():
    return {
        "_id": str(uuid.uuid4()),
        "userid": "user123",
        "transaction_id": fake.bothify(text='TX-#####-????'),
        "status": random.choice(["completed", "pending", "rejected"]),
        "txndate": fake.date_time_between(start_date='-2y', end_date='now').isoformat(),
        "amount": round(random.uniform(500.0, 10000.0), 2),
        "currency": random.choice(["CHF"]),
        "category": random.choice(["Groceries", "Shopping", "Bills", "Entertainment", "Restaurant", "Insurance", "Transport", "Personal", "Donation", "Family"]),
        "payment_channel": random.choice(["Domestic", "SEPA", "International", "Ebill", "InstantPayment"]),
        "receiver": fake.name(),
        "charge": round(random.uniform(0.0, 10.0), 2),     
        "receiver_accountnumber": fake.iban(), 
        "payment_reason": random.choice(["Transfer to Wife", "Electronics Purchase", 
                                         "Telephone Bill", "Mortgage Payment", "Grocery Shopping", "Rent Payment",
                                            "Restaurant", "Clothing", "Healthcare", "Education"
                                         , "Car Repair", "Vacation", "Gift", "Donation", "Other",
                                          "Transfer to Son", "Transfer to Daughter", "Transfer to Friend",])                                         
    }

# Generate and insert 100 mock transactions
transactions = [generate_debit_transaction() for _ in range(1000)]
debit_collection.insert_many(transactions)

print("Inserted 1000 mock debit transactions into the 'transaction' collection.")


# Function to generate a random transaction document
def generate_credit_transaction():
    return {
        "_id": str(uuid.uuid4()),
        "userid": "user123",
        "transaction_id": fake.bothify(text='TX-#####-????'),
        "status": random.choice(["completed"]),
        "txndate": fake.date_time_between(start_date='-2y', end_date='now').isoformat(),
        "amount": round(random.uniform(500.0, 10000.0), 2),
        "currency": random.choice(["CHF"]),
        "sender": fake.name(),        
        "sender_accountnumber": fake.iban(), 
        "payment_reason": random.choice(["Salary", "Bonus", "Refund", "Interest", "Dividend", "Gift", "Other"])                                         
    }

# Generate and insert 100 mock transactions
transactions = [generate_credit_transaction() for _ in range(1000)]
credit_collection.insert_many(transactions)

print("Inserted 1000 mock credit transactions into the 'transaction' collection.")
