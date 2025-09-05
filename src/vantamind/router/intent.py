from __future__ import annotations

import re
from enum import Enum


class Intent(str, Enum):
    IMAGE = "image"
    CODE = "code"
    CHAT = "chat"


IMAGE_PATTERNS = [
    r"\b(image|picture|art|logo|icon|photo|wallpaper|poster)\b",
    r"\b(draw|paint|render|generate)\b.*\b(image|picture|art)\b",
]

CODE_PATTERNS = [
    r"\b(build|create|scaffold|generate|code|app|project)\b",
    r"\b(api|web app|mobile app|cli|game|service)\b",
]


def detect_intent(text: str) -> Intent:
    lower = text.lower()
    for pattern in IMAGE_PATTERNS:
        if re.search(pattern, lower):
            return Intent.IMAGE
    for pattern in CODE_PATTERNS:
        if re.search(pattern, lower):
            return Intent.CODE
    return Intent.CHAT

