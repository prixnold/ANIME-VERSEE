from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class VantaConfig:
    ollama_host: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    ollama_text_model: str = os.environ.get("VANTAMIND_TEXT_MODEL", "mistral")
    ollama_code_model: str = os.environ.get("VANTAMIND_CODE_MODEL", "deepseek-coder:6.7b")
    ollama_image_model: str = os.environ.get("VANTAMIND_IMAGE_MODEL", "flux")

    openai_api_key: str | None = os.environ.get("OPENAI_API_KEY")
    openai_text_model: str = os.environ.get("OPENAI_TEXT_MODEL", "gpt-4o-mini")
    openai_code_model: str = os.environ.get("OPENAI_CODE_MODEL", "gpt-4o-mini")

    request_timeout_seconds: int = int(os.environ.get("VANTAMIND_TIMEOUT", "120"))

