# 4-Week AI Engineer Learning Path — LLM Apps & Agents (OpenAI-first)

## Context

I'm an experienced Python developer becoming an **AI engineer**, focused on **LLM applications and agents** (RAG, chatbots, tool-use, prompt engineering) rather than ML/model-training. Commitment: ~20–25 hrs/week for 4 weeks. Method: **learn by doing**.

Each week ships a real, runnable project that compounds into a deployed capstone. By week 4 I can independently design, build, evaluate, and ship an LLM-powered agent.

**Provider choice:** **OpenAI-first** (I have OpenAI credit) — `openai` SDK, `gpt-*` models, `text-embedding-3-*` embeddings. **Anthropic (Claude)** and **Google Gemini** come later. A core design habit baked in: a **thin provider-abstraction layer** (`llm.py`) that wraps chat/embeddings behind one interface, so switching providers is a config change, not a rewrite.

**Framework stance:** Build directly on the OpenAI SDK to learn the primitives (chat completions, streaming, function-calling loop, structured outputs) before reaching for frameworks. LangChain/LlamaIndex/OpenAI Agents SDK are optional comparisons once I understand what they abstract.

---

## Setup

- Python 3.11+, a virtualenv, `pip` or `uv`.
- `OPENAI_API_KEY` set in env (or a local `.env`).
- `pip install -r requirements.txt`.
- **Model picks** (use the newest your account has; these are defaults):
  - Workhorse: `gpt-4.1` (or `gpt-4o`)
  - Cheap/fast: `gpt-4.1-mini` (or `gpt-4o-mini`) — classification, high-volume, evals
  - Reasoning: an `o`-series model (e.g. `o4-mini`)
  - Embeddings: `text-embedding-3-small` (→ `-large` if recall is weak)
- Commit daily — this repo is the portfolio.

**Anchor references:** OpenAI docs (Text generation, Function calling, Structured outputs, Embeddings, Responses API, Agents); OpenAI Cookbook; Anthropic's *"Building effective agents"* post (provider-neutral conceptual spine); a prompt-engineering guide.

---

## Week 1 — OpenAI API fundamentals + prompting as a discipline
**Goal:** Fluent with the API, streaming, structured outputs, systematic prompting. Ship two CLI tools + the `llm.py` wrapper.

- **Concepts:** chat messages & multi-turn (stateless — resend history), streaming, **structured outputs** (`client.beta.chat.completions.parse` + Pydantic), prompt engineering (role/task clarity, few-shot, delimited sections, what-not-to-do, length, temperature), token counting (`tiktoken`), the `llm.py` abstraction seam.
- **Build:** `chat.py` (streaming multi-turn CLI w/ `ConversationManager`); `extract.py` (messy text → validated Pydantic object); `PROMPTS.md` (before/after prompt notes).
- **Deliverable:** two tools + `llm.py` + `PROMPTS.md`; able to explain each prompt's shape.

## Week 2 — Retrieval-Augmented Generation (RAG)
**Goal:** Q&A app over my own docs that cites sources and abstains when the answer isn't present.

- **Concepts:** embeddings & semantic search, chunking strategies, vector stores (`chromadb`/`faiss`), the RAG loop, grounding & citations, failure modes (bad chunking, low recall, hallucinated citations, lost-in-the-middle).
- **Build:** `ingest.py` (load → chunk → embed → persist), `ask.py` (retrieve top-k → grounded answer with citations + abstain path), `RAG_NOTES.md` (chunking experiment over ~15 questions). Optional: reimplement in LlamaIndex/LangChain to see the abstraction.
- **Deliverable:** `rag/` app + `RAG_NOTES.md`.

## Week 3 — Tool use & agents
**Goal:** An **agent loop** — model picks tools, I execute, feed results back, repeat.

- **Concepts:** function calling (tool name/description/JSON-schema params), the agentic loop (build manually first), `tool_choice`, parallel tool calls, tool errors as results, when an agent vs. a workflow, gating destructive actions. Optional: OpenAI Agents SDK / Responses API built-in tools.
- **Build:** manual tool-use loop (calculator, web fetch/search, file reader) with a visible reasoning trace; a capstone-seed agent (research or codebase) that uses the week-2 RAG retriever as a tool; guardrails (confirmation gate, max-iterations, error recovery).
- **Deliverable:** `agent/` — multi-tool agent with trace + safety rails.

## Week 4 — Evaluation, optimization, shipping (capstone)
**Goal:** Make the agent production-shaped: evaluated, cost-optimized, observable, deployed.

- **Concepts:** **evals** (15–30 cases; programmatic checks + LLM-as-judge; track pass-rate), cost/latency & model selection, structured logging/observability, deployment (FastAPI + streaming, Docker, Render/Railway/Fly). **Multi-provider payoff:** add Claude or Gemini behind `llm.py` and compare on the eval set.
- **Build:** eval harness (baseline → ≥3 measured improvements); logging + cheapest-passing-model selection + second provider comparison; FastAPI streaming endpoint, containerize, deploy; `README` with architecture, eval results, cost-per-request.
- **Deliverable (Capstone):** deployed, evaluated agent with a public URL, an eval report (incl. cross-provider comparison), and a clear README.

---

## End-to-end verification per week
- **W1:** `chat.py` holds a streaming multi-turn convo; `extract.py` returns a valid object every time across 10 inputs; all calls go through `llm.py`.
- **W2:** `ask.py` answers with citations grounded in retrieved chunks, abstains when out-of-corpus.
- **W3:** agent completes a ≥3-tool-call task and asks/refuses before irreversible actions.
- **W4:** eval run prints a pass-rate; deployed endpoint streams over HTTP; logs show per-call tokens+cost; same eval runs against a 2nd provider. Move the number before/after a prompt change.

Run each deliverable yourself (CLI, then HTTP) and watch it work *and* fail.

## After the 4 weeks
Add Gemini as a 3rd backend; go deeper on MCP (build a tool server); multi-agent orchestration; production concerns (prompt-injection defense, PII, caching at scale, batch); publish the capstone + a short blog post on evals.
