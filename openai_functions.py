import json
from datetime import datetime
from pymongo import MongoClient
from typing import Optional, List
from faker import Faker
from dotenv import load_dotenv
import os

# load_dotenv() reads the .env file and sets the environment variables.
load_dotenv()

# Setup Faker and MongoDB connection
fake = Faker()

mongo_pwd = os.getenv("MONGO_PWD")

# MongoDB Connection Setup
mongoclient = MongoClient("mongodb+srv://antjohns:"+mongo_pwd+"@cluster0.cw6ev.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongoclient["payments"]  # Replace with your database name
collection = db["debit_transaction"]


function_search_transactions = {
    "name": "search_transactions",
    "description": "Search for user payment transaction based on various criteria most of them are optional. By default transactions are sorted by txndate. i.e it shows recent txns first. The transactions are debit ones which are the transactions where the user is the sender.",    
    "parameters": {
        "type": "object",
        "properties": {
            
            "date_from": {
                "type": "string",
                "format": "date-time",
                "description": "The start date to filter transactions, formatted as an ISO 8601 datetime string.",
            },
            
            "date_to": {
                "type": "string",
                "format": "date-time",
                "description": "The end date to filter transactions, formatted as an ISO 8601 datetime string.",
            },
            "status": {
                "type": "string",
                "description": "The status of the transaction (e.g., 'completed', 'pending', 'failed').",
            },
            "currency": {
                "type": "string",
                "description": "The currency used in the transaction (e.g., 'CHF').",
            },
           
            "receiver": {
                "type": "string",
                "description": "The name of the receiver or beneficiary of the transaction.",
            },
            "receiver_accountnumber": {
                "type": "string",
                "description": "The account number of the receiver in the transaction in IBAN format.",
            },
            "min_amount": {
                "type": "number",
                "description": "The minimum transaction amount to filter.",
            },
            "max_amount": {
                "type": "number",
                "description": "The maximum transaction amount to filter.",
            },
            "payment_reason": {
                "type": "string",
                "description": "A regex pattern to filter transactions based on the payment reason. The search is case-insensitive.",
            },
            "limit": {
                "type": "integer",
                "description": "The maximum number of transactions to return.",               
            },

        },
        "required": [],
    },
}

def search_transactions(
    transaction_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[str] = None,
    currency: Optional[str] = None,
    receiver: Optional[str] = None,
    receiver_accountnumber: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    payment_reason: Optional[str] = None,
    limit: Optional[int] = 100  # Default limit to the last 10 transactions
) -> List[dict]:
    
    # Build the query dictionary dynamically
    print(f"Searching transactions with params: {locals()}")
    query = {}    

    # Hardcoded fields to exclude from the returned result
    projection = {
        "category": 0,
        "payment_channel": 0,
        "receiver_accountnumber": 0,
        "charge": 0,       
        "transaction_id": 0,
    }
    
    if date_from and date_to:
        query["txndate"] = {"$gte": date_from.isoformat(), "$lte": date_to.isoformat()}
    elif date_from:
        query["txndate"] = {"$gte": date_from.isoformat()}
    elif date_to:
        query["txndate"] = {"$lte": date_to.isoformat()}
    if status:
        query["status"] = status
    if transaction_id:
        query["transaction_id"] = transaction_id
        # clear all the fields in the projection if transaction_id is provided
        projection = {}
    if currency:
        query["currency"] = currency
    if receiver:
        query["receiver"] = receiver
        # clear all the fields in the projection
        projection = {}
    if receiver_accountnumber:
        query["receiver_accountnumber"] = receiver_accountnumber
        projection["receiver_accountnumber"] = 1
    if min_amount and max_amount:
        query["amount"] = {"$gte": min_amount, "$lte": max_amount}
    elif min_amount:
        query["amount"] = {"$gte": min_amount}
    elif max_amount:
        query["amount"] = {"$lte": max_amount}
    if limit:
        limit = int(limit)
    
    # Update to use text search for payment_reason
    if payment_reason:
        query["$text"] = {"$search": payment_reason}
    
    # Execute the query
    if limit is None:
        results = list(collection.find(query,projection).sort("txndate", -1))
    else:
        results = list(collection.find(query,projection).sort("txndate", -1).limit(limit))

    # Reformat the txndate to dd mm yyyy format in the returned results
    for transaction in results:
        if 'txndate' in transaction:
            transaction['txndate'] = datetime.fromisoformat(transaction['txndate']).strftime('%d %m %Y')

    return results

def create_transaction(       
    amount: float,
    currency: str,    
    receiver: str,
    receiver_accountnumber: str,
    payment_reason: Optional[str] = None
) -> dict:
    # Build the transaction dictionary
    transaction = {
        "userid": "user123",        
        "status": "completed",
        "txndate": datetime.now().isoformat(),
        "amount": amount,       
        "currency": currency,
        "category": "Other",
        "payment_channel": "Domestic",
        "receiver": receiver,
        "receiver_accountnumber": receiver_accountnumber,
        "payment_reason": payment_reason
    }

    # Insert the transaction into the MongoDB collection
    result = collection.insert_one(transaction)
    transaction["_id"] = str(result.inserted_id)
    
    return transaction

function_create_transaction = {
    "name": "create_transaction",
    "description": "Create a new debit payment transaction for user. This is a debit transaction where the user is the sender.",
    "parameters": {
        "type": "object",
        "properties": {           
            "amount": {
                "type": "number",
                "description": "The amount of the transaction.",
            },
            "currency": {
                "type": "string",
                "description": "The currency used in the transaction (e.g., 'USD', 'EUR').",
            },            
            "receiver": {
                "type": "string",
                "description": "The name of the receiver in the transaction.",
            },
            "payment_reason": {
                "type": "string",
                "description": "The reason for the payment.",
            },
            "receiver_accountnumber": {
                "type": "string",
                "description": "The account number of the receiver in the transaction in IBAN format. This is mandatory.",
            },
        },
        "required": ["amount", "currency", "receiver", "payment_reason","receiver_accountnumber"],
    },
}


def call_search_transactions (response, messages):
    # Extract the tool call response
    toolcall_response_message = response.choices[0].message
    # Extract the arguments from the tool call
    arguments = json.loads(toolcall_response_message.tool_calls[0].function.arguments)
    # Extract the parameters
    # Convert the date strings to datetime objects
    if "date_from" in arguments:
        arguments["date_from"] = datetime.fromisoformat(arguments["date_from"].replace("Z", "+00:00"))
    if "date_to" in arguments:
        arguments["date_to"] = datetime.fromisoformat(arguments["date_to"].replace("Z", "+00:00"))
    # Call the function with the extracted parameters
    results = search_transactions(**arguments)
        # Handle empty results
    if not results:
        results = [{"message": "No transactions found based on the provided criteria."}]
    
    print('This is a debug message')
    print(results)

    for result in results:
        if '_id' in result:
            del result['_id']

    function_call_result_message = {
        "role": "tool",
        "content": json.dumps(results),
         "tool_call_id": toolcall_response_message.tool_calls[0].id
    }
    messages.append(toolcall_response_message)
    messages.append(function_call_result_message)
    return messages


def call_create_transaction(response, messages):
    # Extract the tool call response
    toolcall_response_message = response.choices[0].message
    # Extract the arguments from the tool call
    arguments = json.loads(toolcall_response_message.tool_calls[0].function.arguments)
    
    # Call the function with the extracted parameters
    new_transaction = create_transaction(**arguments)
    
    function_call_result_message = {
        "role": "tool",
        "content": json.dumps(new_transaction),
        "tool_call_id": toolcall_response_message.tool_calls[0].id
    }
    messages.append(toolcall_response_message)
    messages.append(function_call_result_message)
    return messages
