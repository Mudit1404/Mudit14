import streamlit as st
import requests
from gtts import gTTS
import os
import re
from pydub import AudioSegment
from io import BytesIO

# --- Config ---
PERPLEXITY_API_KEY = "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"  # Replace with your key
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
MODEL_NAME = "mistral-7b-instruct"  # or "codellama-13b-instruct", etc.


def clean_script_for_tts(raw_script: str) -> str:
    cleaned_lines = []
    for line in raw_script.split("\n"):
        line = line.strip()
        if re.fullmatch(r"\*.*?\*", line) or re.fullmatch(r"\(.*?\)", line) or not line:
            continue
        line = re.sub(r"\*.*?\*", "", line)
        line = re.sub(r"\(.*?\)", "", line)
        if line.strip():
            cleaned_lines.append(line)
    return " ".join(cleaned_lines)


st.title("🎧 KUKU Companion – Personalized Audio Stories")

mood = st.selectbox("What's your current mood?", ["Motivated", "Calm", "Romantic", "Curious", "Emotional"])
story_lang = st.radio("Choose story language:", ["English", "Hindi"])

if st.button("🎙️ Generate My Story"):
    with st.spinner("Crafting your immersive long story..."):

        prompt_text = (
            f"Write a deep, immersive audio story in {story_lang.lower()} for someone feeling {mood.lower()}. "
            f"The story should be suitable for a 10-minute narration (at least 1000–1200 words). "
            f"Include layered storytelling with chapters or emotional phases. "
            f"Use rich descriptions, natural dialogue, and an engaging progression of events. "
            f"Subtly weave in sound cues like *light footsteps*, *wind whispering*, *rain falling*, *heartbeats*, etc. "
            f"Write in a poetic and engaging tone that feels like it is being personally told to the listener. "
            f"No technical instructions, just natural storytelling as for an audio drama."
        )

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt_text}],
            "temperature": 0.8,
            "max_tokens": 2048
        }

        try:
            # Send the API request
            res = requests.post(PERPLEXITY_URL, headers=headers, json=payload)
            
            # Check if the response status code is 200
            res.raise_for_status()

            # Process the response
            story = res.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()

            if not story:
                st.error("No story was generated. Please try again.")
                st.stop()

            cleaned_story = clean_script_for_tts(story)
            word_count = len(cleaned_story.split())

            if word_count < 150:
                st.error("The generated story is too short. Please try again.")
                st.stop()

            st.subheader("📖 Original Story")
            st.text_area("", story, height=300)

            st.subheader("🧼 Cleaned Story for Audio")
            st.text_area("", cleaned_story, height=200)

            # Background music paths (ensure filenames are all lowercase!)
            mood_music_paths = {
                "motivated": "bg_music/motivated.mp3",
                "calm": "bg_music/calm.mp3",
                "romantic": "bg_music/romantic.mp3",
                "curious": "bg_music/curious.mp3",
                "emotional": "bg_music/emotional.mp3"
            }

            lang_code = "hi" if story_lang == "Hindi" else "en"
            tts = gTTS(text=cleaned_story, lang=lang_code)
            speech_io = BytesIO()
            tts.write_to_fp(speech_io)
            speech_io.seek(0)

            speech_audio = AudioSegment.from_mp3(speech_io)

            bg_music_path = mood_music_paths.get(mood.lower())
            if not bg_music_path or not os.path.exists(bg_music_path):
                raise FileNotFoundError(f"Background music not found for mood: {mood}")

            bg_audio = AudioSegment.from_mp3(bg_music_path) - 10
            bg_audio *= (len(speech_audio) // len(bg_audio) + 1)
            bg_audio = bg_audio[:len(speech_audio)]

            final_audio = speech_audio.overlay(bg_audio)
            output_io = BytesIO()
            final_audio.export(output_io, format="mp3")
            output_io.seek(0)

            st.subheader("🔊 Your Personalized Audio with Background Music")
            st.audio(output_io)

        except requests.exceptions.HTTPError as e:
            # If there's a 400 error, show a message with the response
            st.error(f"An error occurred: {e.response.json().get('message', 'Unknown error occurred')}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
