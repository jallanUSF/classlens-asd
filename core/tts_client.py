"""
Edge TTS wrapper — synthesizes dialogue lines to MP3 using Microsoft Edge voices.

Design: TTS is commodity plumbing. Gemma does all the reasoning (script writing);
Edge TTS is the "printer" that turns text into audio. No API key, no cost,
300+ voices across 70+ languages.

MP3 concatenation is done by raw byte append — Edge TTS returns single-stream
MP3 frames that play correctly when concatenated without re-encoding in
Chrome, Firefox, and Safari.
"""

from __future__ import annotations

import asyncio
from typing import Iterable

# Host, Guest voice pair per language. Keep these stable — they become part of
# the product's voice identity. Edge TTS voice names are documented at
# https://learn.microsoft.com/azure/ai-services/speech-service/language-support
VOICES: dict[str, tuple[str, str]] = {
    "en": ("en-US-JennyNeural", "en-US-GuyNeural"),
    "es": ("es-MX-DaliaNeural", "es-MX-JorgeNeural"),
    "vi": ("vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"),
    "zh": ("zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"),
}


def voices_for(language: str) -> tuple[str, str]:
    """Return (host_voice, guest_voice) for a language code. Falls back to English."""
    return VOICES.get(language, VOICES["en"])


async def _synthesize_async(text: str, voice: str) -> bytes:
    """Internal async synth — Edge TTS is an async streaming API."""
    import edge_tts  # lazy import so test suite can mock without the dep installed

    communicate = edge_tts.Communicate(text, voice)
    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


def synthesize_line(text: str, voice: str) -> bytes:
    """Synthesize a single text line to MP3 bytes using the given Edge voice."""
    return asyncio.run(_synthesize_async(text, voice))


def concatenate_mp3(chunks: Iterable[bytes]) -> bytes:
    """Concatenate MP3 byte chunks. Edge TTS frames are playable when joined raw."""
    return b"".join(chunks)


def synthesize_script(script: list[dict], language: str = "en") -> bytes:
    """Synthesize a full Host/Guest script to a single concatenated MP3.

    Args:
        script: list of {"speaker": "host"|"guest", "text": str}
        language: ISO language code; picks voice pair from VOICES.
    Returns:
        Concatenated MP3 bytes ready to write to disk.
    """
    host_voice, guest_voice = voices_for(language)
    chunks: list[bytes] = []
    for line in script:
        speaker = line.get("speaker", "host")
        text = (line.get("text") or "").strip()
        if not text:
            continue
        voice = host_voice if speaker == "host" else guest_voice
        chunks.append(synthesize_line(text, voice))
    return concatenate_mp3(chunks)
