"""
GemmaClient: Thin wrapper around Google AI Studio's Gemini API for Gemma 4.
Supports: text, multimodal (image+text), function calling, thinking mode.

All agents talk to Gemma 4 through this single interface.
"""

import os
import json
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class GemmaClient:
    """Single interface for all Gemma 4 interactions."""

    def __init__(self, model: str = "gemma-4-27b-it"):
        api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_AI_STUDIO_KEY not set. Copy .env.example to .env and add your key."
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Basic text generation."""
        config = types.GenerateContentConfig(
            system_instruction=system
        ) if system else None
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return response.text

    def generate_multimodal(
        self,
        image_path: str,
        prompt: str,
        system: Optional[str] = None,
    ) -> str:
        """Image + text -> text. Used by Vision Reader."""
        image_bytes = Path(image_path).read_bytes()

        # Detect mime type from extension
        ext = Path(image_path).suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
        mime_type = mime_map.get(ext, "image/jpeg")

        contents = [
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(text=prompt),
        ]
        config = types.GenerateContentConfig(
            system_instruction=system
        ) if system else None
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        return response.text

    def generate_with_tools(
        self,
        prompt: str,
        tools: list,
        system: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> dict:
        """
        Function calling. Used by Vision Reader (with image), IEP Mapper, and Material Forge.

        Returns:
            {"function": name, "args": {...}} if function call succeeded
            {"text": response_text} if model returned text instead
        """
        config = types.GenerateContentConfig(
            system_instruction=system,
            tools=tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="AUTO"
                )
            ),
        )

        # Build contents: optional image + text prompt
        if image_path:
            image_bytes = Path(image_path).read_bytes()
            ext = Path(image_path).suffix.lower()
            mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
            mime_type = mime_map.get(ext, "image/jpeg")
            contents = [
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                types.Part.from_text(text=prompt),
            ]
        else:
            contents = prompt

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        # Extract function call results
        for part in response.candidates[0].content.parts:
            if hasattr(part, "function_call") and part.function_call:
                return {
                    "function": part.function_call.name,
                    "args": dict(part.function_call.args),
                }
        return {"text": response.text}

    def generate_with_thinking(
        self,
        prompt: str,
        system: Optional[str] = None,
    ) -> dict:
        """
        Thinking mode. Used by Progress Analyst.

        Returns:
            {"thinking": reasoning_chain, "output": final_response}
        """
        config = types.GenerateContentConfig(
            system_instruction=system,
            thinking_config=types.ThinkingConfig(
                thinking_budget_tokens=2048
            ),
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        # Separate thinking from final response
        thinking = ""
        output = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, "thought") and part.thought:
                thinking += part.text
            else:
                output += part.text
        return {"thinking": thinking, "output": output}
