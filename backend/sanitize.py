"""
Shared sanitization and credential-checking utilities for backend routers.

Extracted from chat.py, alerts.py, and trajectory.py to eliminate duplication.
"""

import os
import re

# Strip any HTML/XML-like tags the model emits. Gemma occasionally leaks
# table fragments (<td>, <tr>) and structural tags from training data.
# We also drop <script>/<style> *blocks* with their contents, since leaving
# their bodies as plain text would leak raw CSS/JS into the chat UI.
_SCRIPT_STYLE_BLOCK_RE = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL
)
_ANY_TAG_RE = re.compile(r"<[^>]+>")


def sanitize_model_text(text: str) -> str:
    """Remove HTML tags and dangerous script/style blocks from model output."""
    if not text:
        return text
    text = _SCRIPT_STYLE_BLOCK_RE.sub("", text)
    text = _ANY_TAG_RE.sub("", text)
    return text.strip()


def has_real_model_credentials() -> bool:
    """True if any live-model provider API key is configured."""
    return bool(
        os.getenv("OPENROUTER_API_KEY")
        or (
            os.getenv("GOOGLE_AI_STUDIO_KEY")
            and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here"
        )
    )
