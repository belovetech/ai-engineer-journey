"""Thin provider-abstraction layer.

Everything in the project talks to the model through THESE functions instead of
importing `openai` directly. That keeps provider-specific code in one place, so
adding Anthropic (Claude) or Gemini later (week 4) is a change here — not a
rewrite of every script.

Public API:
    chat(messages, model=None, stream=False, **opts) -> str | Iterator[str]
    parse(messages, response_format, model=None, **opts) -> <Pydantic instance>
    embed(texts, model=None) -> list[list[float]]
"""

from __future__ import annotations

import os
from typing import Iterator

from dotenv import load_dotenv
from openai import OpenAI

# Load OPENAI_API_KEY (and optional overrides) from a local .env if present.
load_dotenv()

# Sensible defaults — override per call or via env vars. Swap to the newest
# model IDs your account has access to (gpt-4o, o4-mini, etc.).
DEFAULT_CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4.1")
DEFAULT_EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# Single client, reused. Reads OPENAI_API_KEY from the environment.
_client = OpenAI()


def chat(messages: list[dict], model: str | None = None, stream: bool = False, **opts):
    """Send a chat conversation and return the assistant's reply.

    messages: [{"role": "system"|"user"|"assistant", "content": str}, ...]
    stream=False -> returns the full reply as a str
    stream=True  -> returns an iterator of text chunks (for live CLI output)
    """
    model = model or DEFAULT_CHAT_MODEL
    if stream:
        return _chat_stream(messages, model, **opts)
    resp = _client.chat.completions.create(model=model, messages=messages, **opts)
    return resp.choices[0].message.content


def _chat_stream(messages: list[dict], model: str, **opts) -> Iterator[str]:
    response = _client.chat.completions.create(
        model=model, messages=messages, stream=True, **opts
    )
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def parse(messages: list[dict], response_format, model: str | None = None, **opts):
    """Structured output: returns a validated instance of `response_format`
    (a Pydantic model). The model is constrained to your schema, so you get a
    typed object back instead of hand-parsing JSON.
    """
    model = model or DEFAULT_CHAT_MODEL
    completion = _client.beta.chat.completions.parse(
        model=model, messages=messages, response_format=response_format, **opts
    )
    return completion.choices[0].message.parsed


def embed(texts, model: str | None = None) -> list[list[float]]:
    """Return a list of embedding vectors, one per input string. (Used in week 2.)"""
    model = model or DEFAULT_EMBED_MODEL
    if isinstance(texts, str):
        texts = [texts]
    resp = _client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]
