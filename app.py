import streamlit as st
import random
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

from pprint import pprint
from pymongo import MongoClient
from typing import Optional, List
from datetime import datetime
import json
from faker import Faker
import logging

from openai_functions import (
    function_search_transactions,
    function_create_transaction,
    call_search_transactions,
    call_create_transaction
)


load_dotenv()
# Setup Faker and MongoDB connection
fake = Faker()

client = OpenAI(api_key=os.getenv("OPKEY"))


def getopenairesponse(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function", "function": function_search_transactions},
               {"type": "function", "function": function_create_transaction}])  
    return response

 
st.title("Banking AI Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

messages=[                
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
    ]

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        #response = st.write_stream(response_generator())
        
        response =  getopenairesponse(messages=messages)

        # if content is None then it is a tool call and response_message.tool_calls[0].function.name will be the function name
        if response.choices[0].message.content is None:
            
            if response.choices[0].message.tool_calls[0].function.name == "search_transactions":
                newmessages = call_search_transactions(response, messages)
            elif response.choices[0].message.tool_calls[0].function.name == "create_transaction":
                newmessages = call_create_transaction(response, messages) 

            newresponse = getopenairesponse(newmessages)
            # Add the results to the chat history
            new_assistant_response = newresponse.choices[0].message.content
            st.markdown(new_assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": new_assistant_response})
        else:
            # Display the assistant response
            assistant_response = response.choices[0].message.content
            st.markdown(assistant_response)            
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

