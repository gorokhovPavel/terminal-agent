from __future__ import annotations

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(
    api_key=os.getenv("YANDEX_API_KEY"),
    base_url=os.getenv("YANDEX_BASE_URL", "https://ai.api.cloud.yandex.net/v1"),
)

_MODEL_URI = os.getenv("YANDEX_MODEL_URI")
_TEMPERATURE = float(os.getenv("YANDEX_TEMPERATURE", "0.4"))
_MAX_TOKENS = int(os.getenv("YANDEX_MAX_TOKENS", "10000"))


def call_model(messages: list, tools: list | None = None):
    kwargs = {
        "model": _MODEL_URI,
        "messages": messages,
        "temperature": _TEMPERATURE,
        "max_tokens": _MAX_TOKENS,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = _client.chat.completions.create(**kwargs)
    return response.choices[0].message
