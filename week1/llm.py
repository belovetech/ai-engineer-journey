"""Thin provider-abstraction layer.

Everything in the project talks to the model through THESE functions instead of
importing `openai` directly. That keeps provider-specific code in one place, so
adding Anthropic (Claude) or Gemini later (week 4) is a change here — not a
rewrite of every script.

Public API:
    chat(messages, model=None, stream=False, **opts) -> str | Iterator[str]
    parse(messages, response_format, model=None, **opts) -> <Pydantic instance>
    embed(texts, model=None) -> list[list[float]]
    count_tokens(text, model=None) -> int
    count_message_tokens(messages, model=None) -> int
    estimate_cost(input_tokens, output_tokens, model=None) -> float | None
"""

from __future__ import annotations

import json
import os
from typing import Iterator

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

# Load OPENAI_API_KEY (and optional overrides) from a local .env if present.
load_dotenv()

# Sensible defaults — override per call or via env vars. Swap to the newest
# model IDs your account has access to (gpt-4o, o4-mini, etc.).
DEFAULT_CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4.1")
DEFAULT_EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# Prices are USD per 1M tokens. Keep this small and explicit so stale prices are
# easy to spot and update from https://openai.com/api/pricing/.
MODEL_PRICES_PER_1M = {
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

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


def count_tokens(text: str, model: str | None = None) -> int:
    """Estimate text tokens with tiktoken for local cost/context checks."""
    model = model or DEFAULT_CHAT_MODEL
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("o200k_base")
    return len(encoding.encode(text))


def count_message_tokens(messages: list[dict], model: str | None = None) -> int:
    """Estimate chat message tokens.

    This serializes the message list before tokenizing. It is good enough for
    learning and cost awareness, but the API's billed count can differ because
    request formatting, response schemas, and tools add hidden tokens.
    """
    serialized = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    return count_tokens(serialized, model=model)


def estimate_cost(
    input_tokens: int, output_tokens: int, model: str | None = None
) -> float | None:
    """Estimate USD cost from local token counts and the known price table."""
    model = model or DEFAULT_CHAT_MODEL
    prices = MODEL_PRICES_PER_1M.get(model)
    if prices is None:
        return None
    return (
        input_tokens * prices["input"] / 1_000_000
        + output_tokens * prices["output"] / 1_000_000
    )


def format_usage_estimate(
    input_tokens: int, output_tokens: int, model: str | None = None
) -> str:
    """Return a compact, human-readable token and cost estimate."""
    model = model or DEFAULT_CHAT_MODEL
    estimated_cost = estimate_cost(input_tokens, output_tokens, model=model)
    if estimated_cost is None:
        cost = "unknown price"
    else:
        cost = f"${estimated_cost:.6f}"
    return (
        f"model={model}, input_tokens~{input_tokens}, "
        f"output_tokens~{output_tokens}, estimated_cost={cost}"
    )
