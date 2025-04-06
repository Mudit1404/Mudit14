
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import re
import requests
from pydub import AudioSegment
from io import BytesIO


def clean_script_for_tts(raw_script: str) -> str:
    cleaned_lines = []
    for line in raw_script.split("\n"):
        line = line.strip()

        # Skip lines that are only sound cues or formatting
        if re.fullmatch(r"\*.*?\*", line):
            continue
        if re.fullmatch(r"\(.*?\)", line):
            continue
        if not line:
            continue

        # Remove inline sound cues like *footsteps*
        line = re.sub(r"\*.*?\*", "", line)
        line = re.sub(r"\(.*?\)", "", line)

        # Only keep non-empty, clean lines
        if line.strip():
            cleaned_lines.append(line)

    return " ".join(cleaned_lines)


# Gemini setup
genai.configure(api_key="AIzaSyBqSSu4DlfaSD4Kcpe-hQR5Px8o7e_blKA")

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

        st.subheader("📖 Original Story")
        st.text_area("", final_story, height=300)

        st.subheader("🧼 Cleaned Story for Audio")
        st.text_area("", cleaned_story, height=200)

        # Background music URLs
        mood_music_urls = {
            "motivated": "https://github.com/Mudit1404/Mudit14/blob/a5884aa8c1b7e02fcb053e223fa2a8c693b43f64/Kuku-FM/bg_music/motivated.mp3",
            "calm": "https://github.com/Mudit1404/Mudit14/blob/a5884aa8c1b7e02fcb053e223fa2a8c693b43f64/Kuku-FM/bg_music/calm.mp3",
            "romantic": "https://github.com/Mudit1404/Mudit14/blob/a5884aa8c1b7e02fcb053e223fa2a8c693b43f64/Kuku-FM/bg_music/romantic.mp3",
            "curious": "https://github.com/Mudit1404/Mudit14/blob/a5884aa8c1b7e02fcb053e223fa2a8c693b43f64/Kuku-FM/bg_music/curious.mp3",
            "emotional": "https://github.com/Mudit1404/Mudit14/blob/a5884aa8c1b7e02fcb053e223fa2a8c693b43f64/Kuku-FM/bg_music/emotional.mp3"
        }

        try:
            # Generate speech
            lang_code = "hi" if story_lang == "Hindi" else "en"
            tts = gTTS(text=cleaned_story, lang=lang_code)

            speech_io = BytesIO()
            tts.write_to_fp(speech_io)
            speech_io.seek(0)

            speech_audio = AudioSegment.from_mp3(speech_io)

            # Load background music from URL
            mood_key = mood.lower()
            url = mood_music_urls.get(mood_key)
            
            if not url:
                raise ValueError(f"No background music URL found for mood: {mood_key}")

            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to download background music for mood '{mood_key}'. Status code: {response.status_code}")

            bg_audio = AudioSegment.from_mp3(BytesIO(response.content))
            bg_audio = bg_audio - 10  # lower bg music volume
            bg_audio = bg_audio * (len(speech_audio) // len(bg_audio) + 1)
            bg_audio = bg_audio[:len(speech_audio)]

            # Combine and export to memory
            final_audio = speech_audio.overlay(bg_audio)
            output_io = BytesIO()
            final_audio.export(output_io, format="mp3")
            output_io.seek(0)

            st.subheader("🔊 Your Personalized Audio with Background Music")
            st.audio(output_io)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
