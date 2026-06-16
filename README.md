# ai-engineer-journey

A build-first, 4-week path to becoming an **AI engineer** focused on **LLM apps & agents**.
Provider: **OpenAI-first** (Claude + Gemini added later via the `llm.py` seam).

See **[LEARNING_PLAN.md](./LEARNING_PLAN.md)** for the full curriculum.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # paste your OPENAI_API_KEY into .env
```

## Progress

| Week | Theme | Folder | Status |
|------|-------|--------|--------|
| 1 | API fundamentals + prompting | [`week1/`](./week1) | scaffolded — start here |
| 2 | Retrieval-Augmented Generation | `week2/` | upcoming |
| 3 | Tool use & agents | `week3/` | upcoming |
| 4 | Evals, optimization & shipping | `week4/` | upcoming |

## Week 1 — run it

```bash
python week1/chat.py
echo "Jane Doe, jane@co.com, wants the Enterprise plan, asked for a demo" | python week1/extract.py
```

See [`week1/README.md`](./week1/README.md) for the full setup and this week's checklist.
