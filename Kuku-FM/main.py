import streamlit as st
import openai
from gtts import gTTS
import os
import re
from pydub import AudioSegment
from io import BytesIO

# 🔐 Set your OpenAI API key here (or load from env)
openai.api_key = "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"  # Replace with your actual key

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

# Streamlit UI
st.title("🎧 KUKU Companion – Personalized Audio Stories")

mood = st.selectbox("What's your current mood?", ["Motivated", "Calm", "Romantic", "Curious", "Emotional"])
story_lang = st.radio("Choose story language:", ["English", "Hindi"])

if st.button("🎙️ Generate My Story"):
    with st.spinner("Crafting your immersive long story..."):
        prompt_text = (
            f"Write a deep, immersive audio story in {story_lang.lower()} for someone feeling {mood.lower()}. "
            f"The story should be suitable for a 10-minute narration (around 1000–1200 words). "
            f"Include layered storytelling with chapters or emotional phases. "
            f"Use rich descriptions, natural dialogue, and an engaging progression of events. "
            f"Subtly weave in sound cues like *light footsteps*, *wind whispering*, *rain falling*, *heartbeats*, etc. "
            f"Write in a poetic, engaging tone like an audio drama. Do not include instructions or technical content."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.8,
                max_tokens=2048
            )
            final_story = response.choices[0].message.content.strip()
            cleaned_story = clean_script_for_tts(final_story)
            word_count = len(cleaned_story.split())

            if word_count < 150:
                st.error("The generated story is too short. Please try again.")
                st.stop()

            st.subheader("📖 Original Story")
            st.text_area("", final_story, height=300)

            st.subheader("🧼 Cleaned Story for Audio")
            st.text_area("", cleaned_story, height=200)

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

            mood_key = mood.lower()
            bg_music_path = mood_music_paths.get(mood_key)

            if not bg_music_path or not os.path.exists(bg_music_path):
                raise FileNotFoundError(f"Background music not found for mood: {mood}")

            bg_audio = AudioSegment.from_mp3(bg_music_path) - 10
            bg_audio = bg_audio * (len(speech_audio) // len(bg_audio) + 1)
            bg_audio = bg_audio[:len(speech_audio)]

            final_audio = speech_audio.overlay(bg_audio)
            output_io = BytesIO()
            final_audio.export(output_io, format="mp3")
            output_io.seek(0)

            st.subheader("🔊 Your Personalized Audio with Background Music")
            st.audio(output_io)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
