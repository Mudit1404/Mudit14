import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import re
from pydub import AudioSegment
from io import BytesIO
import requests

# Clean script: removes only stage directions and formatting
def clean_script_for_tts(raw_script: str) -> str:
    # Remove content between asterisks
    text = re.sub(r'\*[^*]+\*', '', raw_script)
    # Remove content between parentheses
    text = re.sub(r'\([^)]+\)', '', text)
    # Remove any remaining asterisks
    text = text.replace('*', '')
    # Split into lines, clean and rejoin
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    return ' '.join(lines)

# Gemini setup
genai.configure(api_key="AIzaSyAcba9ishOsQbrkNHA6Mv-DnhoPTreZPuU")

st.title("🎧 KUKU Companion – Personalized Audio Stories")

# User Inputs
mood = st.selectbox("What's your current mood?", ["Motivated", "Calm", "Romantic", "Curious", "Emotional"])
story_lang = st.radio("Choose story language:", ["English", "Hindi"])

if st.button("🎙️ Generate My Story"):
    with st.spinner("Crafting your immersive long story..."):
        prompt_text = (
            f"Write a deep, immersive audio story in {story_lang.lower()} for someone feeling {mood.lower()}. "
            f"The story should be suitable for a 10-minute narration (at least 1000–1200 words). "
            f"Include layered storytelling with chapters or emotional phases. "
            f"Use rich descriptions, natural dialogue, and an engaging progression of events. "
            f"Subtly weave in sound cues like *light footsteps*, *wind whispering*, *rain falling*, *heartbeats*, etc., to enhance the immersion. "
            f"Write in a poetic and engaging tone that feels like it is being personally told to the listener. "
            f"No technical instructions, just natural storytelling as for an audio drama."
        )

        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        max_retries = 2
        final_story = ""
        cleaned_story = ""
        word_count = 0

        for attempt in range(max_retries):
            response = model.generate_content(prompt_text)
            final_story = response.text.strip()
            cleaned_story = clean_script_for_tts(final_story)
            word_count = len(cleaned_story.split())

            if word_count >= 500:
                break

        if word_count < 150:
            st.error("The generated story is too short even after retries. Please try again later.")
            st.stop()

        story = final_story

        st.subheader("📖 Original Story")
        st.text_area("", story, height=300)

        st.subheader("🧼 Cleaned Story for Audio")
        st.text_area("", cleaned_story, height=200)

        # Select background music from GitHub raw URLs
        mood_music = {
            "Motivated": "https://raw.githubusercontent.com/Mudit1404/Mudit14/Main/Kuku-FM/bg_music/motivated.mp3",
            "Calm": "https://raw.githubusercontent.com/Mudit1404/Mudit14/Main/Kuku-FM/bg_music/calm.mp3",
            "Romantic": "https://raw.githubusercontent.com/Mudit1404/Mudit14/Main/Kuku-FM/bg_music/romantic.mp3",
            "Curious": "https://raw.githubusercontent.com/Mudit1404/Mudit14/Main/Kuku-FM/bg_music/curious.mp3",
            "Emotional": "https://raw.githubusercontent.com/Mudit1404/Mudit14/Main/Kuku-FM/bg_music/emotional.mp3"
        }

        try:
            # Generate speech audio
            lang_code = "hi" if story_lang == "Hindi" else "en"
            tts = gTTS(text=cleaned_story, lang=lang_code)

            # Save speech audio to BytesIO
            speech_io = BytesIO()
            tts.write_to_fp(speech_io)
            speech_io.seek(0)

            # Load background music from GitHub URL
            bg_music_url = mood_music[mood]
            response = requests.get(bg_music_url)
            
            # Load audio files with pydub
            speech_audio = AudioSegment.from_mp3(speech_io)
            bg_audio = AudioSegment.from_mp3(BytesIO(response.content))

            # Adjust background volume and duration
            bg_audio = bg_audio - 10  # Reduce volume by 10dB
            bg_audio = bg_audio * (len(speech_audio) // len(bg_audio) + 1)  # Loop if needed
            bg_audio = bg_audio[:len(speech_audio)]  # Match speech length

            # Combine audio
            combined = speech_audio.overlay(bg_audio)

            # Export to BytesIO
            output_io = BytesIO()
            combined.export(output_io, format="mp3")
            output_io.seek(0)

            st.subheader("🔊 Your Personalized Audio")
            st.audio(output_io)

        except requests.exceptions.RequestException as e:
            st.error(f"Error downloading background music: {str(e)}")
        except Exception as e:
            st.error(f"Error generating audio: {str(e)}")

def add_background_music(narration_file: str, mood: str) -> str:
    # Map moods to background music URLs
    mood_music = {
        "Motivated": "https://github.com/anars/blank-audio/blob/master/250-milliseconds-of-silence.mp3?raw=true",  # Replace with actual URLs
        "Calm": "https://github.com/anars/blank-audio/blob/master/250-milliseconds-of-silence.mp3?raw=true",
        "Romantic": "https://github.com/anars/blank-audio/blob/master/250-milliseconds-of-silence.mp3?raw=true",
        "Curious": "https://github.com/anars/blank-audio/blob/master/250-milliseconds-of-silence.mp3?raw=true",
        "Emotional": "https://github.com/anars/blank-audio/blob/master/250-milliseconds-of-silence.mp3?raw=true"
    }

    try:
        import requests
        from io import BytesIO

        # Load narration
        narration = AudioSegment.from_mp3(narration_file)

        # Download and load background music
        bg_music = requests.get(mood_music[mood])
        bg_audio = AudioSegment.from_mp3(BytesIO(bg_music.content))

        # Process background music
        bg_audio = bg_audio - 20  # Reduce volume
        bg_audio = bg_audio * (len(narration) // len(bg_audio) + 1)  # Loop if needed
        bg_audio = bg_audio[:len(narration)]  # Match narration length

        # Combine audio
        combined = narration.overlay(bg_audio)

        output_path = "final_audio_with_bg.mp3"
        combined.export(output_path, format="mp3")
        return output_path

    except Exception as e:
        st.error(f"Error adding background music: {str(e)}")
        return narration_file  # Return original narration if there's an error
