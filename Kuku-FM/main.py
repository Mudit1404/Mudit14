import os
import openai
from gtts import gTTS
import re
from openai import OpenAI
from pydub import AudioSegment
from io import BytesIO

# Get the API key from environment variables (GitHub Secrets)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API Key not found! Please check your GitHub Secrets.")

client = OpenAI(api_key=api_key)

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

# Your Streamlit UI code follows...
