import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient
from faker import Faker
import random

# Setup Faker and MongoDB connection
fake = Faker()
# client = MongoClient("mongodb+srv://antjohns: @cluster0.cw6ev.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["payments"]  # Replace with your database name
debit_collection = db["debit_transaction"]
credit_collection = db["credit_transaction"]

# db.debit_transaction.createIndex( { payment_reason: "text", receiver: "text" }, { weights: { payment_reason: 2, receiver: 1 } } )

# Function to generate a random transaction document
def generate_debit_transaction():
    return {
        "_id": str(uuid.uuid4()),
        "userid": "user123",
        "transaction_id": fake.bothify(text='TX-#####-????'),
        "status": random.choice(["completed"]),
        "txndate": fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
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


# Function to generate a debit transaction with optional custom values
def generate_custom_debit_transaction(
    userid="user123", 
    transaction_id=None, 
    status=None, 
    txndate=None, 
    amount=None, 
    currency="CHF", 
    category=None, 
    payment_channel=None, 
    receiver=None, 
    charge=None, 
    receiver_accountnumber=None, 
    payment_reason=None
):
    return {
        "_id": str(uuid.uuid4()),
        "userid": userid,
        "transaction_id": transaction_id if transaction_id else fake.bothify(text='TX-#####-????'),
        "status": status if status else random.choice(["completed", "pending", "rejected"]),
        "txndate": txndate if txndate else fake.date_time_between(start_date='-1m', end_date='now').isoformat(),
        "amount": amount if amount else round(random.uniform(500.0, 10000.0), 2),
        "currency": currency,
        "category": category if category else random.choice(["Groceries", "Shopping", "Bills", "Entertainment", "Restaurant", "Insurance", "Transport", "Personal", "Donation", "Family"]),
        "payment_channel": payment_channel if payment_channel else random.choice(["Domestic", "SEPA", "International", "Ebill", "InstantPayment"]),
        "receiver": receiver if receiver else fake.name(),
        "charge": charge if charge else round(random.uniform(0.0, 10.0), 2),
        "receiver_accountnumber": receiver_accountnumber if receiver_accountnumber else fake.iban(),
        "payment_reason": payment_reason if payment_reason else random.choice([
            "Transfer to Wife", "Electronics Purchase", "Telephone Bill", "Mortgage Payment", "Grocery Shopping", "Rent Payment",
            "Restaurant", "Clothing", "Healthcare", "Education", "Car Repair", "Vacation", "Gift", "Donation", "Other",
            "Transfer to Son", "Transfer to Daughter", "Transfer to Friend",
        ])
    }


def generate_many_transactions():     
    # Generate and insert 100 mock transactions
    transactions = [generate_debit_transaction() for _ in range(100)]
    debit_collection.insert_many(transactions)
    print("Inserted 100 mock debit transactions into the 'transaction' collection.")


# Example: Inserting a single transaction with some custom values
custom_transaction = generate_custom_debit_transaction(
    userid="user456",
    amount=1500.50,
    status="completed",
    payment_reason="Electricity Bill",
    receiver="Zurich Power Company",
    category="Bills",
    payment_channel="Ebill"
)

# Insert the custom transaction into the collection
debit_collection.insert_one(custom_transaction)

generate_many_transactions()



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
# transactions = [generate_credit_transaction() for _ in range(1000)]
# credit_collection.insert_many(transactions)

# print("Inserted 1000 mock credit transactions into the 'transaction' collection.")
