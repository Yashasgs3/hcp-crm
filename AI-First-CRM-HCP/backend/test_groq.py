import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("MODEL_NAME", "gemma2-9b-it")

print(f"API Key: {api_key[:20]}...{api_key[-8:] if len(api_key) > 8 else ''}")
print(f"Model: {model}")

from groq import Groq
client = Groq(api_key=api_key)
try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "say hi"}],
        max_tokens=10
    )
    print(f"SUCCESS: {response.choices[0].message.content}")
except Exception as e:
    print(f"ERROR: {e}")
