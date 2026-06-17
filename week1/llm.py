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
    active_chat_model(model=None) -> str
"""

from __future__ import annotations

import json
import os
from typing import Iterator

import tiktoken
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

# Load OPENAI_API_KEY (and optional overrides) from a local .env if present.
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
DEFAULT_CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4.1")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
DEFAULT_EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
DEFAULT_GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

MODEL_PRICES_PER_1M = {
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gemini-3.1-flash-lite": {"input": 0.025, "output": 0.10},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-2.0-flash-lite": {"input": 0.025, "output": 0.10},
}

_openai_client: OpenAI | None = None
_gemini_client: genai.Client | None = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client


def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is required when LLM_PROVIDER=gemini. "
                "Create a key in Google AI Studio and add it to your .env."
            )
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


def active_chat_model(model: str | None = None) -> str:
    """Return the model name for the active provider."""
    if model:
        return model
    if LLM_PROVIDER == "gemini":
        return DEFAULT_GEMINI_MODEL
    return DEFAULT_CHAT_MODEL


def chat(messages: list[dict], model: str | None = None, stream: bool = False, **opts):
    """Send a chat conversation and return the assistant's reply.

    messages: [{"role": "system"|"user"|"assistant", "content": str}, ...]
    stream=False -> returns the full reply as a str
    stream=True  -> returns an iterator of text chunks (for live CLI output)
    """
    model = active_chat_model(model)
    if LLM_PROVIDER == "gemini":
        if stream:
            return _gemini_chat_stream(messages, model, **opts)
        return _gemini_chat(messages, model, **opts)
    if stream:
        return _openai_chat_stream(messages, model, **opts)
    resp = _get_openai_client().chat.completions.create(
        model=model, messages=messages, **opts
    )
    return resp.choices[0].message.content


def _openai_chat_stream(messages: list[dict], model: str, **opts) -> Iterator[str]:
    response = _get_openai_client().chat.completions.create(
        model=model, messages=messages, stream=True, **opts
    )
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def _gemini_parts(messages: list[dict]) -> tuple[str | None, list[types.Content]]:
    """Convert OpenAI-style messages to Gemini system instruction + contents."""
    system_parts: list[str] = []
    contents: list[types.Content] = []
    for message in messages:
        role = message["role"]
        text = message["content"]
        if role == "system":
            system_parts.append(text)
            continue
        gemini_role = "model" if role == "assistant" else "user"
        contents.append(
            types.Content(role=gemini_role, parts=[types.Part(text=text)])
        )
    system_instruction = "\n\n".join(system_parts) if system_parts else None
    return system_instruction, contents


def _gemini_config(messages: list[dict], **opts) -> types.GenerateContentConfig:
    system_instruction, _ = _gemini_parts(messages)
    config = types.GenerateContentConfig(system_instruction=system_instruction)
    if "temperature" in opts:
        config.temperature = opts["temperature"]
    if "max_tokens" in opts:
        config.max_output_tokens = opts["max_tokens"]
    if "max_output_tokens" in opts:
        config.max_output_tokens = opts["max_output_tokens"]
    return config


def _gemini_chat(messages: list[dict], model: str, **opts) -> str:
    _, contents = _gemini_parts(messages)
    response = _get_gemini_client().models.generate_content(
        model=model,
        contents=contents,
        config=_gemini_config(messages, **opts),
    )
    return response.text or ""


def _gemini_chat_stream(messages: list[dict], model: str, **opts) -> Iterator[str]:
    _, contents = _gemini_parts(messages)
    stream = _get_gemini_client().models.generate_content_stream(
        model=model,
        contents=contents,
        config=_gemini_config(messages, **opts),
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text


def parse(messages: list[dict], response_format, model: str | None = None, **opts):
    """Structured output: returns a validated instance of `response_format`
    (a Pydantic model). The model is constrained to your schema, so you get a
    typed object back instead of hand-parsing JSON.
    """
    model = active_chat_model(model)
    if LLM_PROVIDER == "gemini":
        return _gemini_parse(messages, response_format, model, **opts)
    completion = _get_openai_client().beta.chat.completions.parse(
        model=model, messages=messages, response_format=response_format, **opts
    )
    return completion.choices[0].message.parsed


def _gemini_parse(messages: list[dict], response_format, model: str, **opts):
    _, contents = _gemini_parts(messages)
    config = _gemini_config(messages, **opts)
    config.response_mime_type = "application/json"
    config.response_schema = response_format
    response = _get_gemini_client().models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
    if response.parsed is not None:
        return response.parsed
    return response_format.model_validate_json(response.text or "{}")


def embed(texts, model: str | None = None) -> list[list[float]]:
    """Return a list of embedding vectors, one per input string."""
    if isinstance(texts, str):
        texts = [texts]
    if LLM_PROVIDER == "gemini":
        return _gemini_embed(texts, model)
    model = model or DEFAULT_EMBED_MODEL
    resp = _get_openai_client().embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


def _gemini_embed(texts: list[str], model: str | None = None) -> list[list[float]]:
    model = model or DEFAULT_GEMINI_EMBED_MODEL
    result = _get_gemini_client().models.embed_content(
        model=model,
        contents=texts,
    )
    return [e.values for e in result.embeddings]


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
