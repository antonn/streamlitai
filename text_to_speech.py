import streamlit as st
from pathlib import Path
import os
import base64

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI()

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )


# Define the Streamlit app
def main():
    st.title("Text to Speech Demo with OpenAI")

    # Input text
    text_input = st.text_area("Enter the text you want to convert to speech:", 
                              value="Today is a wonderful day to build something people love!")

    # Voice selection
    voice = st.selectbox("Select a voice:", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])

    # File name input
    file_name = st.text_input("Enter the output file name:", value="speech.mp3")

    # Button to trigger text-to-speech conversion
    if st.button("Convert to Speech"):
        if text_input.strip() == "":
            st.error("Please enter some text to convert.")
        else:
            try:
                # Define the output file path
                speech_file_path = Path(__file__).parent / file_name
                
                # Perform the text-to-speech conversion
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text_input
                )
                                
                # Stream the response to a file
                response.write_to_file(speech_file_path)
                
                st.success(f"Speech file saved successfully: {speech_file_path}")
                   # Play the generated audio file in the Streamlit app
                audio_file = open(speech_file_path, "rb")
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3",autoplay=True)
                st.write("Auto playing the audio:")
                #autoplay_audio(speech_file_path)
            except Exception as e:
                print(e)
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
