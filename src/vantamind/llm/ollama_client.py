from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests


class OllamaClient:
    """Minimal HTTP client for interacting with a local Ollama server."""

    def __init__(self, base_url: Optional[str] = None, timeout_seconds: float = 120.0) -> None:
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code < 500
        except Exception:
            return False

    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        response = requests.post(url, json=payload, timeout=self.timeout_seconds)
        response.raise_for_status()
        data = response.json()
        # Newer Ollama returns { message: { content } }, older may return { response }
        if "message" in data and isinstance(data["message"], dict):
            return data["message"].get("content", "")
        return data.get("response", "")

    def generate(self, model: str, prompt: str, temperature: float = 0.2) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        response = requests.post(url, json=payload, timeout=self.timeout_seconds)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

