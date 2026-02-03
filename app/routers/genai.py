from fastapi import APIRouter, Request
from pydantic import BaseModel
import requests
import os

router = APIRouter()

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY

class TestGenRequest(BaseModel):
    requirements: str
    filename: str  # e.g., "tests/TagAI/tagaitests.spec.ts"

@router.post("/genai/generate-test")
def generate_test(request: TestGenRequest):
    prompt = f"Generate a Playwright test file based on these requirements: {request.requirements}\nOutput only valid Playwright test code."
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_API_URL, json=payload)
    if response.ok:
        data = response.json()
        # Extract code from Gemini response
        code = ""
        try:
            code = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return {"error": "Could not parse Gemini response."}
        # Save code to file
        file_path = os.path.join(os.getcwd(), request.filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        return {"status": "success", "filename": request.filename, "code": code}
    return {"error": "Gemini API call failed.", "details": response.text}
