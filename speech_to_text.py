import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text
from datetime import datetime
from openai import OpenAI
client = OpenAI()

state = st.session_state

if 'text_received' not in state:
    state.text_received = []

c1, c2 = st.columns(2)
with c1:
    st.write("How can I help you:")
with c2:
    text = speech_to_text(language='en', use_container_width=True, just_once=True, key='STT')

if text:
    state.text_received.append(text)

for text in state.text_received:
    st.text(text)

st.write("Record your voice, and play the recorded audio:")
audio = mic_recorder(start_prompt="⏺️", stop_prompt="⏹️", key='recorder', format="wav")

if audio:
    st.audio(audio['bytes'])
    # Save the audio to a file
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"audio_recording_{current_time}.wav"
    
    with open(file_name, "wb") as f:
        f.write(audio['bytes'])

    st.success(f"Audio saved as {file_name}")

    with open(file_name, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
          model="whisper-1", 
          file=audio_file
        )
        translation = client.audio.translations.create(
            model="whisper-1", 
            file=audio_file
            )
        
        # Display the transcription text
    st.write(transcription.text)

    st.write('\n\n')

    st.write(translation.text)
