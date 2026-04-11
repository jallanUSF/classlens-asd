"""
GemmaClient: Thin wrapper around Google AI Studio's Gemini API for Gemma 4.
Supports: text, multimodal (image+text), function calling, thinking mode, streaming.

Provider backends:
  - google (default): Google AI Studio via google.genai
  - openrouter: OpenRouter via OpenAI-compatible API
  - ollama: Local Ollama via OpenAI-compatible API

All agents talk to Gemma 4 through this single interface.
"""

import base64
import os
import json
import logging
from pathlib import Path
from typing import Iterator, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Provider detection
# ---------------------------------------------------------------------------

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "google").lower()

# Default models per provider
_DEFAULT_MODELS = {
    "google": "gemma-4-31b-it",
    "openrouter": os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b-it"),
    "ollama": os.getenv("OLLAMA_MODEL", "gemma3:27b"),
}


class GemmaClient:
    """Single interface for all Gemma 4 interactions."""

    def __init__(self, model: str | None = None, provider: str | None = None):
        self.provider = (provider or MODEL_PROVIDER).lower()
        self.model = model or _DEFAULT_MODELS.get(self.provider, _DEFAULT_MODELS["google"])

        if self.provider == "google":
            self._init_google()
        elif self.provider in ("openrouter", "ollama"):
            self._init_openai_compat()
        else:
            raise ValueError(
                f"Unknown MODEL_PROVIDER '{self.provider}'. "
                "Valid options: google, openrouter, ollama"
            )

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    def _init_google(self):
        """Set up Google AI Studio client."""
        from google import genai
        api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_AI_STUDIO_KEY not set. Copy .env.example to .env and add your key."
            )
        self.client = genai.Client(api_key=api_key)

    def _init_openai_compat(self):
        """Set up OpenAI-compatible client (OpenRouter or Ollama)."""
        from openai import OpenAI

        if self.provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENROUTER_API_KEY not set. Copy .env.example to .env and add your key."
                )
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
        else:  # ollama
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self.client = OpenAI(
                base_url=base_url,
                api_key="ollama",  # Ollama ignores this but the SDK requires it
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Basic text generation."""
        if self.provider == "google":
            return self._google_generate(prompt, system)
        return self._openai_generate(prompt, system)

    def generate_multimodal(
        self,
        image_path: str,
        prompt: str,
        system: Optional[str] = None,
    ) -> str:
        """Image + text -> text. Used by Vision Reader.

        On OpenRouter/Ollama this sends the image as a base64 data URL via the
        OpenAI vision API. If the model doesn't support vision, it falls back
        to text-only with a note that the image could not be processed.
        """
        if self.provider == "google":
            return self._google_generate_multimodal(image_path, prompt, system)
        return self._openai_generate_multimodal(image_path, prompt, system)

    def generate_with_tools(
        self,
        prompt: str,
        tools: list,
        system: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> dict:
        """
        Function calling.

        Returns:
            {"function": name, "args": {...}} if function call succeeded
            {"text": response_text} if model returned text instead
        """
        if self.provider == "google":
            return self._google_generate_with_tools(prompt, tools, system, image_path)
        return self._openai_generate_with_tools(prompt, tools, system, image_path)

    def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
    ) -> Iterator[str]:
        """
        Streaming text generation. Yields text chunks as the model produces them.

        Used by the chat endpoint for Server-Sent Events. On providers without
        native streaming the generator yields the full response as a single chunk.
        """
        if self.provider == "google":
            yield from self._google_generate_stream(prompt, system)
        else:
            yield from self._openai_generate_stream(prompt, system)

    def generate_with_thinking(
        self,
        prompt: str,
        system: Optional[str] = None,
    ) -> dict:
        """
        Thinking mode. Used by Progress Analyst.

        On non-Google providers this falls back to a normal generation
        and returns an empty thinking chain.

        Returns:
            {"thinking": reasoning_chain, "output": final_response}
        """
        if self.provider == "google":
            return self._google_generate_with_thinking(prompt, system)
        # Fallback: regular generation, no thinking mode available
        logger.info(
            "Thinking mode not available on %s; falling back to standard generation.",
            self.provider,
        )
        output = self._openai_generate(prompt, system)
        return {"thinking": "", "output": output}

    # ==================================================================
    # Google AI Studio implementation (original code, unchanged)
    # ==================================================================

    def _google_generate(self, prompt: str, system: Optional[str] = None) -> str:
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=system
        ) if system else None
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return response.text

    def _google_generate_multimodal(
        self, image_path: str, prompt: str, system: Optional[str] = None
    ) -> str:
        from google.genai import types
        image_bytes = Path(image_path).read_bytes()
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

    def _google_generate_with_tools(
        self, prompt: str, tools: list, system: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> dict:
        from google.genai import types
        wrapped_tools = [
            types.Tool(function_declarations=[t]) if isinstance(t, dict) else t
            for t in tools
        ]
        config = types.GenerateContentConfig(
            system_instruction=system,
            tools=wrapped_tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="AUTO"
                )
            ),
        )

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

        for part in response.candidates[0].content.parts:
            if hasattr(part, "function_call") and part.function_call:
                return {
                    "function": part.function_call.name,
                    "args": dict(part.function_call.args),
                }
        return {"text": response.text}

    def _google_generate_stream(
        self, prompt: str, system: Optional[str] = None
    ) -> Iterator[str]:
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=system
        ) if system else None
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            config=config,
        ):
            if chunk.text:
                yield chunk.text

    def _google_generate_with_thinking(
        self, prompt: str, system: Optional[str] = None
    ) -> dict:
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=system,
            thinking_config=types.ThinkingConfig(
                includeThoughts=True
            ),
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        thinking = ""
        output = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, "thought") and part.thought:
                thinking += part.text
            else:
                output += part.text
        return {"thinking": thinking, "output": output}

    # ==================================================================
    # OpenAI-compatible implementation (OpenRouter / Ollama)
    # ==================================================================

    def _openai_generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Text generation via OpenAI-compatible API."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content

    def _openai_generate_stream(
        self, prompt: str, system: Optional[str] = None
    ) -> Iterator[str]:
        """Streaming text generation via OpenAI-compatible API."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta

    def _openai_generate_multimodal(
        self, image_path: str, prompt: str, system: Optional[str] = None
    ) -> str:
        """Vision via OpenAI-compatible API using base64 data URL."""
        image_bytes = Path(image_path).read_bytes()
        ext = Path(image_path).suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
        mime_type = mime_map.get(ext, "image/jpeg")
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": prompt},
            ],
        })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            # If the model doesn't support vision, fall back to text-only
            logger.warning(
                "Multimodal request failed on %s (%s); falling back to text-only.",
                self.provider, e,
            )
            return self._openai_generate(
                f"[Image could not be processed.]\n\n{prompt}", system
            )

    def _openai_generate_with_tools(
        self, prompt: str, tools: list, system: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> dict:
        """Function calling via OpenAI-compatible API."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        # Build user message content (optionally with image)
        if image_path:
            image_bytes = Path(image_path).read_bytes()
            ext = Path(image_path).suffix.lower()
            mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
            mime_type = mime_map.get(ext, "image/jpeg")
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            data_url = f"data:{mime_type};base64,{b64}"
            user_content = [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": prompt},
            ]
        else:
            user_content = prompt

        messages.append({"role": "user", "content": user_content})

        # Convert Google-style tool dicts to OpenAI function-calling format
        openai_tools = self._convert_tools_to_openai(tools)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=openai_tools if openai_tools else None,
            )
            msg = response.choices[0].message

            # Check for tool calls in the response
            if msg.tool_calls:
                tc = msg.tool_calls[0]
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {"raw": tc.function.arguments}
                return {"function": tc.function.name, "args": args}

            return {"text": msg.content or ""}
        except Exception as e:
            logger.warning(
                "Tool calling failed on %s (%s); retrying without tools.",
                self.provider, e,
            )
            # Fallback: ask model to respond as JSON
            fallback_prompt = (
                f"{prompt}\n\nRespond with a JSON object containing your analysis."
            )
            text = self._openai_generate(fallback_prompt, system)
            return {"text": text}

    @staticmethod
    def _convert_tools_to_openai(tools: list) -> list:
        """Convert Google-style function declarations to OpenAI tool format.

        Google format (dict): {"name": ..., "description": ..., "parameters": {...}}
        OpenAI format: {"type": "function", "function": {"name": ..., "description": ..., "parameters": {...}}}
        """
        openai_tools = []
        for t in tools:
            if isinstance(t, dict):
                fn_def = {
                    "name": t.get("name", "unknown"),
                    "description": t.get("description", ""),
                }
                params = t.get("parameters", {})
                # If parameters is already a JSON Schema object, use it directly.
                # Otherwise, build a minimal schema from the flat dict.
                if isinstance(params, dict) and "type" in params:
                    fn_def["parameters"] = params
                elif isinstance(params, dict):
                    # Flat key->description dict; convert to a permissive schema
                    fn_def["parameters"] = {
                        "type": "object",
                        "properties": {
                            k: {"type": "string", "description": str(v)}
                            for k, v in params.items()
                        },
                    }
                openai_tools.append({"type": "function", "function": fn_def})
            # If it's already a google.genai types.Tool, skip (can't convert)
        return openai_tools
