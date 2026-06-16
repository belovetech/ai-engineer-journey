# Week 1 — OpenAI API fundamentals + prompting

**Goal:** get fluent with the chat API, streaming, structured outputs, and
systematic prompting. Everything routes through `llm.py` — the provider seam
that lets you add Claude/Gemini later without touching the app code.

## Setup (once)

From the repo root:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env and paste your OPENAI_API_KEY
```

## Run the tools

```bash
# Streaming multi-turn chatbot ( /reset, /exit )
python week1/chat.py

# Structured extraction: messy text -> validated Contact object
echo "Jane Doe, jane@co.com, wants the Enterprise plan, asked for a demo" | python week1/extract.py
python week1/extract.py somefile.txt
```

## Files

| File         | What it teaches |
|--------------|-----------------|
| `llm.py`     | Provider abstraction: `chat()`, `parse()`, `embed()`. The one place that imports `openai`. |
| `chat.py`    | Multi-turn state (resend history), streaming output. |
| `extract.py` | Structured outputs with Pydantic — reliable typed JSON. |

## This week's checklist

- [ ] Run both tools end-to-end against the real API.
- [ ] `chat.py` holds a coherent multi-turn conversation (it remembers earlier turns).
- [ ] `extract.py` returns a valid object across **10** different messy inputs — zero parse errors.
- [ ] Add a new field to `Contact` and confirm extraction adapts.
- [ ] Try `gpt-4.1-mini` (set `CHAT_MODEL` in `.env`) and compare quality vs. cost.
- [ ] Start `PROMPTS.md`: for one prompt, record a before/after rewrite and what changed in the output.
- [ ] (Stretch) Add token counting with `tiktoken` and print an estimated cost per call.

## What to understand before moving on

- Why the API is **stateless** and you must resend history each turn.
- Why structured outputs beat "please return JSON" prompting.
- How `llm.py` isolates the provider — sketch how you'd add a `claude` backend.
