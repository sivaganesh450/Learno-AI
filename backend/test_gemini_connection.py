
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    print("Testing gemini-2.0-flash...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello, are you working?"
    )
    print(f"Response: {response.text}")
    print("SUCCESS: gemini-2.0-flash is working.")
except Exception as e:
    print(f"Error: {e}")
