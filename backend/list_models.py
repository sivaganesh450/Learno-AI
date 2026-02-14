
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    with open("models.txt", "w") as f:
        f.write("Available Gemini Models:\n")
        for m in genai.list_models():
            if "gemini" in m.name:
                f.write(f"{m.name}\n")
    print("Models written to models.txt")
except Exception as e:
    print(f"Error: {e}")
