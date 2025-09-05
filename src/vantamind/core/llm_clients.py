from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import requests

from .config import VantaConfig


class LLMError(RuntimeError):
    pass


@dataclass
class ChatMessage:
    role: str
    content: str


class BaseLLMClient:
    def chat(self, messages: List[ChatMessage], model: Optional[str] = None, stream: bool = False) -> str:
        raise NotImplementedError

    def generate(self, prompt: str, model: Optional[str] = None, stream: bool = False) -> str:
        messages = [ChatMessage(role="user", content=prompt)]
        return self.chat(messages, model=model, stream=stream)


class OllamaClient(BaseLLMClient):
    def __init__(self, config: VantaConfig) -> None:
        self.config = config
        self.base_url = config.ollama_host.rstrip("/")

    def chat(self, messages: List[ChatMessage], model: Optional[str] = None, stream: bool = False) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model or self.config.ollama_text_model,
            "messages": [m.__dict__ for m in messages],
            "stream": stream,
        }
        try:
            if stream:
                response = requests.post(url, json=payload, timeout=self.config.request_timeout_seconds, stream=True)
                response.raise_for_status()
                parts: List[str] = []
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line.decode("utf-8"))
                        content = data.get("message", {}).get("content", "")
                        parts.append(content)
                    except Exception:
                        continue
                return "".join(parts)
            else:
                response = requests.post(url, json=payload, timeout=self.config.request_timeout_seconds)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except requests.RequestException as exc:
            raise LLMError(f"Ollama chat error: {exc}") from exc

    def text(self, prompt: str, model: Optional[str] = None) -> str:
        return self.generate(prompt, model=model, stream=False)

    def image_generate_to_file(self, prompt: str, output_path: str, model: Optional[str] = None) -> str:
        # Best-effort: some Ollama image models stream base64-encoded images under the 'image' key.
        # If not available, return guidance.
        url = f"{self.base_url}/api/generate"
        selected_model = model or self.config.ollama_image_model
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": True,
        }
        try:
            response = requests.post(url, json=payload, timeout=self.config.request_timeout_seconds, stream=True)
            response.raise_for_status()
            image_b64: Optional[str] = None
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                except Exception:
                    continue
                if "image" in data:
                    image_b64 = data.get("image")
                if data.get("done") and image_b64:
                    break
            if not image_b64:
                return (
                    "No image data received from Ollama. Ensure an image model is installed, e.g.\n"
                    f"  ollama pull {selected_model}\n"
                    "Then re-run the command."
                )
            import base64

            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_b64))
            return f"Image written to {output_path}"
        except requests.RequestException as exc:
            return (
                f"Ollama image generation failed: {exc}\n"
                f"Try pulling a compatible model: ollama pull {selected_model}"
            )


class OpenAIClient(BaseLLMClient):
    def __init__(self, config: VantaConfig) -> None:
        self.config = config
        self.api_key = config.openai_api_key
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    def chat(self, messages: List[ChatMessage], model: Optional[str] = None, stream: bool = False) -> str:
        if not self.api_key:
            raise LLMError("Missing OPENAI_API_KEY")
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model or self.config.openai_text_model,
            "messages": [m.__dict__ for m in messages],
            "temperature": 0.2,
            "stream": stream,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            if stream:
                response = requests.post(url, json=payload, headers=headers, timeout=self.config.request_timeout_seconds, stream=True)
                response.raise_for_status()
                parts: List[str] = []
                for line in response.iter_lines():
                    if not line:
                        continue
                    if line.startswith(b"data: "):
                        data_str = line[len(b"data: "):].decode("utf-8").strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            parts.append(delta)
                        except Exception:
                            continue
                return "".join(parts)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=self.config.request_timeout_seconds)
                response.raise_for_status()
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except requests.RequestException as exc:
            raise LLMError(f"OpenAI chat error: {exc}") from exc


def get_llm_client(config: VantaConfig, prefer: str = "auto") -> BaseLLMClient:
    # prefer can be 'ollama', 'openai', or 'auto'
    if prefer == "ollama":
        return OllamaClient(config)
    if prefer == "openai":
        return OpenAIClient(config)
    # auto: prefer Ollama if reachable
    try:
        health = requests.get(config.ollama_host.rstrip("/") + "/api/tags", timeout=1)
        if health.ok:
            return OllamaClient(config)
    except Exception:
        pass
    if config.openai_api_key:
        return OpenAIClient(config)
    # default to Ollama client even if offline; errors will be informative
    return OllamaClient(config)

