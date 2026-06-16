# Handoff / Context

Short note so a fresh agent (or future me) can pick up seamlessly after switching
into the `ai-engineer-journey` Conductor workspace.

## What this repo is
A build-first, 4-week path to becoming an AI engineer focused on **LLM apps & agents**.
Learner: experienced Python dev, ~20–25 hrs/week, learn-by-doing.

## Key decisions
- **Provider: OpenAI-first** (learner has OpenAI credit). Anthropic (Claude) and
  Google Gemini are added later — week 4 — behind the `llm.py` abstraction.
- **No framework to start.** Build on the raw OpenAI SDK to learn primitives;
  LangChain/LlamaIndex/OpenAI Agents SDK are optional comparisons later.
- Everything routes through `week1/llm.py` (`chat` / `parse` / `embed`) so adding
  a provider is a change in one file, not a rewrite.
- Full curriculum: **[LEARNING_PLAN.md](./LEARNING_PLAN.md)**.

## Status
- ✅ Repo scaffolded; **Week 1** files created and verified (imports, `Contact`
  schema, `ConversationManager` — tested with a dummy key, no real API call).
- ✅ A `.venv` exists with deps installed (gitignored).
- ⏭️ **Next:** the learner runs the Week 1 tools with a real `OPENAI_API_KEY` and
  works the checklist in [`week1/README.md`](./week1/README.md):
  10 extraction inputs with zero parse errors, add a `Contact` field, try
  `gpt-4.1-mini`, start `PROMPTS.md`.

## How to resume
```bash
source .venv/bin/activate      # or recreate: python -m venv .venv && pip install -r requirements.txt
cp .env.example .env           # paste a real OPENAI_API_KEY
python week1/chat.py
echo "Jane Doe, jane@co.com, wants the Enterprise plan, asked for a demo" | python week1/extract.py
```

## Notes
- Default models: `gpt-4.1` (chat), `text-embedding-3-small` (embeddings).
  Override via `CHAT_MODEL` / `EMBED_MODEL` in `.env` — no code change.
- These files were originally scaffolded from a different Conductor workspace, so
  the cross-session chat history did not transfer — this file + LEARNING_PLAN.md
  carry the context instead.
