# Week 2 — Retrieval-Augmented Generation (RAG)

**Goal:** Build a Q&A app over your own documents that cites sources and
abstains when the answer isn't present. Everything routes through `llm.py` —
embeddings use OpenAI or Gemini based on `LLM_PROVIDER`.

## Setup (once)

From the repo root:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the tools

```bash
# 1. Ingest documents into ChromaDB
python week2/ingest.py                    # ingest week2/docs/
python week2/ingest.py /path/to/docs/     # ingest a custom directory

# 2. Ask questions against the ingested corpus
python week2/ask.py "What is the return policy?"
python week2/ask.py "What are the API rate limits?"
echo "How much PTO do employees get?" | python week2/ask.py
```

## Switching providers

Embeddings route through `llm.embed()` which respects `LLM_PROVIDER`:

```bash
# Ingest with Gemini embeddings
LLM_PROVIDER=gemini python week2/ingest.py

# Query with Gemini (must match the provider used for ingestion)
LLM_PROVIDER=gemini python week2/ask.py "What is NovaPay?"
```

**Important:** The embedding provider used for ingestion must match the one
used for querying. If you ingest with OpenAI embeddings, query with OpenAI.
If you want to compare, re-ingest with the other provider.

## Files

| File | What it teaches |
|------|-----------------|
| `ingest.py` | Document loading (text, markdown, PDF), chunking, embedding, vector store persistence. |
| `ask.py` | Semantic retrieval, grounded prompt construction, citation formatting, abstention. |
| `docs/` | Sample documents for testing (product FAQ, technical spec, company policy, quarterly report). |
| `RAG_NOTES.md` | Chunking experiments and observations. |

## This week's checklist

- [ ] Ingest all sample docs with `ingest.py` — zero errors.
- [ ] `ask.py` answers with `[source: filename]` citations grounded in retrieved chunks.
- [ ] `ask.py` abstains for out-of-corpus questions (e.g. "What is the weather today?").
- [ ] Compare OpenAI vs Gemini embeddings on the same set of questions.
- [ ] Experiment with chunk sizes (200 vs 500 vs 1000 words) and document results.
- [ ] Experiment with top-k (3 vs 5 vs 10) and observe retrieval quality.
- [ ] Record at least one failure mode (bad chunking, wrong chunk, hallucinated citation).
- [ ] Write up experiments in `RAG_NOTES.md`.

## What to understand before moving on

- Why embeddings enable semantic search (not just keyword matching).
- How chunking strategy affects retrieval quality.
- Why the prompt must instruct the model to abstain — it won't do it by default.
- The difference between retrieval quality and generation quality.
