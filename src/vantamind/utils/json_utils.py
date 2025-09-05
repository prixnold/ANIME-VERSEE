from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional


def extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    """Extract the first JSON object found in the text.

    Looks for the first {...} block and attempts to parse it.
    """
    # Try markdown fenced blocks first
    fenced = re.findall(r"```json\s*(\{[\s\S]*?\})\s*```", text)
    candidates = fenced if fenced else re.findall(r"(\{[\s\S]*\})", text)
    for cand in candidates:
        try:
            return json.loads(cand)
        except Exception:
            continue
    return None

