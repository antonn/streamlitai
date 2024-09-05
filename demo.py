import streamlit as st
import random
import time
from openai import OpenAI
from dotenv import load_dotenv
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from pathlib import Path
import os
import base64
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

# Intialize current date and time
current_datetime = datetime.now()

system_messages = [
    {"role": "system", "content": "You are a helpful customer support of a bank to assist in user queries related to their transactions. Please strictly ignore any questions which are not banking relevant with polite reply." +
      "Use the supplied tools to assist the user. Please note that current date and time is " + current_datetime.strftime("%Y-%m-%d %H:%M:%S") +
      ". As this is a voice assistant please answer in clear and concise sentences and in brief as possible."
      },
    ]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = system_messages
    st.session_state.newsidebarInput = False

def readoutloud(assistant_response):
    try:
                # Define the output file path
                speech_file_path = Path(__file__).parent / "speech.mp3"
                
                # Perform the text-to-speech conversion
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=assistant_response
                )
                                
                # Stream the response to a file
                response.write_to_file(speech_file_path)
                
                # st.success(f"Speech file saved successfully: {speech_file_path}")
                # Play the generated audio file in the Streamlit app
                audio_file = open(speech_file_path, "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3",autoplay=True)
                #st.write("Auto playing the audio:")
                #autoplay_audio(speech_file_path)
    except Exception as e:
                print(e)
                st.error(f"An error occurred: {e}")

def airesponse(messages):
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
            readoutloud(new_assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": new_assistant_response})
    else:
            # Display the assistant response
            assistant_response = response.choices[0].message.content
            st.markdown(assistant_response)            
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            readoutloud(assistant_response)
            


# Add a sidebar with text input
sidebar_input = ""

with st.sidebar:
    st.write("Speak to the Assistant:")
    audio = mic_recorder(start_prompt="⏺️", stop_prompt="🛑", key='recorder', format="wav")

    #file_name = st.text_input("Enter the output file name:", value="speech.mp3")

    if audio:
        st.audio(audio['bytes'])
        # Save the audio to a file
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"audio_recording_{current_time}.wav"

        with open(file_name, "wb") as f:
            f.write(audio['bytes'])

        # Load and process the audio file for transcription
        with open(file_name, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        # Display the transcription text
        # st.write(f"Transcribed Text: {transcription.text}")
        sidebar_input = transcription.text


# If sidebar input is provided, append it as a user message
if sidebar_input:
    st.session_state.messages.append({"role": "user", "content": sidebar_input})
    st.session_state.newsidebarInput = True
    

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    messages=[                
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
    ]
if st.session_state.newsidebarInput:
    airesponse(messages)
    st.session_state.newsidebarInput = False



# Accept user input from the main chat input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        airesponse(st.session_state.messages)
