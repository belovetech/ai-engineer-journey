# Week 1 — OpenAI API fundamentals + prompting

**Goal:** get fluent with the chat API, streaming, structured outputs, and
systematic prompting. Everything routes through `llm.py` — the provider seam
that lets you swap between OpenAI and Gemini without touching the app code.

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

## Switching providers

By default the tools use OpenAI (`gpt-4.1`). To use Gemini instead, set
`LLM_PROVIDER=gemini` — either in `.env` or inline:

```bash
# Chat with Gemini
LLM_PROVIDER=gemini python week1/chat.py

# Extract with Gemini
echo "Jane Doe, jane@co.com, wants the Enterprise plan" | LLM_PROVIDER=gemini python week1/extract.py
```

Both providers produce the same interface — only `llm.py` changes under the hood.

### Testing both providers

**OpenAI (default):**

```bash
python week1/chat.py
# Type a message, verify streaming works, usage line shows model=gpt-4.1
# /exit

echo "Aisha Bello, Head of Operations at NovaPay, aisha@novapay.com, wants a demo of the Enterprise plan." | python week1/extract.py
# Verify JSON output + cost estimate on stderr
```

**Gemini:**

```bash
LLM_PROVIDER=gemini python week1/chat.py
# Same prompts — verify streaming works, usage line shows model=gemini-3.1-flash-lite
# /exit

echo "Aisha Bello, Head of Operations at NovaPay, aisha@novapay.com, wants a demo of the Enterprise plan." | LLM_PROVIDER=gemini python week1/extract.py
# Verify same JSON schema, usage shows gemini model + pricing
```

**Side-by-side comparison:**

```bash
echo "Priya Shah, Product Manager at Contoso, priya@contoso.com, asked for a walkthrough of the Team plan." | python week1/extract.py
echo "---"
echo "Priya Shah, Product Manager at Contoso, priya@contoso.com, asked for a walkthrough of the Team plan." | LLM_PROVIDER=gemini python week1/extract.py
```

Both should produce matching structured output, proving the abstraction works.

## Files

| File         | What it teaches |
|--------------|-----------------|
| `llm.py`     | Provider abstraction: `chat()`, `parse()`, `embed()`. Routes to OpenAI or Gemini based on `LLM_PROVIDER`. |
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
