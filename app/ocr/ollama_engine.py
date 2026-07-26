from __future__ import annotations

import base64
from pathlib import Path

from openai import OpenAI

from app.core.config import settings


def _image_to_data_url(image_path: Path) -> str:
    extension = image_path.suffix.lower().lstrip(".")
    mime_type = "jpeg" if extension in {"jpg", "jpeg"} else extension
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/{mime_type};base64,{encoded}"


def transcribe_with_ollama(image_path: Path) -> str:
    client = OpenAI(
        base_url=f"{settings.ollama_base_url.rstrip('/')}/",
        api_key="ollama",
        timeout=settings.ollama_timeout_seconds,
    )
    prompt = (
        "Transcribe exactly the handwritten Spanish text in this image. "
        "Preserve line breaks, accents, punctuation, and numbering. "
        "Do not summarize or translate. Return only the transcription."
    )
    response = client.chat.completions.create(
        model=settings.ollama_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": _image_to_data_url(image_path)}},
                ],
            }
        ],
        temperature=settings.ollama_temperature,
        max_tokens=settings.ollama_max_output_tokens,
    )
    text = response.choices[0].message.content or ""
    return text.strip()
