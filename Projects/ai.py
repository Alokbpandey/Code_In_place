# ai.py

import openai
import os
from dotenv import load_dotenv

# Load your .env file that contains OPENAI_API_KEY
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_gpt(prompt: str, model: str = "gpt-4", temperature: float = 0.7) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"⚠️ Error during GPT call: {str(e)}"
