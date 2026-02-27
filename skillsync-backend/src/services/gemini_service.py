from typing import Any, Dict
import requests

class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://gemini.googleapis.com/v1"

    def generate_response(self, prompt: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "max_tokens": 150
        }
        response = requests.post(f"{self.base_url}/generate", headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def analyze_text(self, text: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "text": text
        }
        response = requests.post(f"{self.base_url}/analyze", headers=headers, json=data)
        response.raise_for_status()
        return response.json()