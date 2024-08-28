import json
from datetime import datetime
from pymongo import MongoClient
from typing import Optional, List
from faker import Faker



# Setup Faker and MongoDB connection
fake = Faker()

# MongoDB Connection Setup
mongoclient = MongoClient("mongodb+srv://antjohns:PASSWORDHERE@cluster0.cw6ev.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongoclient["payments"]  # Replace with your database name
collection = db["transaction"]

function_create_transaction = {
    "name": "create_transaction",
    "description": "Create or Enter a new payment transaction in user transaction table of the bank.",
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
                "description": "The account number of the receiver in the transaction in IBAN format.",
            },
        },
        "required": ["amount", "currency", "receiver", "payment_reason","receiver_accountnumber"],
    },
}

function_search_transactions = {
    "name": "search_transactions",
    "description": "Search for transactions in the MongoDB collection based on various criteria.",
    "parameters": {
        "type": "object",
        "properties": {
            "userid": {
                "type": "string",
                "description": "The user ID associated with the transaction.",
            },
            "user_accountnumber": {
                "type": "string",
                "description": "The account number of the user associated with the transaction.",
            },
            "date_from": {
                "type": "string",
                "format": "date-time",
                "description": "The start date to filter transactions, formatted as an ISO 8601 datetime string.",
            },
            "creditdebit": {
                "type": "string",
                "description": "The credit or debit type of the transaction. Debit means money is taken from the account, and credit means money is added to the account. (e.g., 'credit', 'debit')",               
                 
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
                "description": "The currency used in the transaction (e.g., 'USD', 'EUR').",
            },
            "transactionmode": {
                "type": "string",
                "description": "The mode of the transaction (e.g., 'online', 'offline', 'mobile').",
            },
            "receiver": {
                "type": "string",
                "description": "The name of the receiver in the transaction.",
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
            }
        },
        "required": [],
    },
}

def search_transactions(
    userid: Optional[str] = None,
    user_accountnumber: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[str] = None,
    currency: Optional[str] = None,
    creditdebit: Optional[str] = None,
    transactionmode: Optional[str] = None,
    receiver: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    payment_reason: Optional[str] = None
) -> List[dict]:
    
    # Build the query dictionary dynamically
    query = {}    
    
    if date_from and date_to:
        query["txndate"] = {"$gte": date_from.isoformat(), "$lte": date_to.isoformat()}
    elif date_from:
        query["txndate"] = {"$gte": date_from.isoformat()}
    elif date_to:
        query["txndate"] = {"$lte": date_to.isoformat()}
    if status:
        query["status"] = status
    if currency:
        query["currency"] = currency
    if creditdebit:
        query["creditdebit"] = creditdebit
    if transactionmode:
        query["transactionmode"] = transactionmode
    if receiver:
        query["receiver"] = receiver
    if min_amount and max_amount:
        query["amount"] = {"$gte": min_amount, "$lte": max_amount}
    elif min_amount:
        query["amount"] = {"$gte": min_amount}
    elif max_amount:
        query["amount"] = {"$lte": max_amount}
    if payment_reason:
        query["payment_reason"] = {"$regex": payment_reason, "$options": "i"}

    # Execute the query
    results = list(collection.find(query))
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
        "userid": 282493,
        "user_accountnumber": "10203040",
        "status": "completed",
        "txndate": datetime.now().isoformat(),
        "amount": amount,
        "creditdebit": "debit",
        "currency": currency,
        "transactionmode": "aibot",
        "receiver": receiver,
        "receiver_accountnumber": fake.iban(),
        "payment_reason": payment_reason
    }

    # Insert the transaction into the MongoDB collection
    result = collection.insert_one(transaction)
    transaction["_id"] = str(result.inserted_id)
    
    return transaction

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
        "content": json.dumps(results[0]),
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
