import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiProvider:
    def generate(self, message: str, model: str = None):
        response = client.models.generate_content(
            model=model or "gemini-2.5-flash",
            contents=message,
        )

        return response.text