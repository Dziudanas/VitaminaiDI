from google import genai
from google.genai.types import HttpOptions

API_KEY = ""  # Put your Gemini API key here

client = genai.Client(api_key=API_KEY, http_options=HttpOptions(api_version="v1"))

def get_recommendation(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=prompt,
    )
    return response.text
