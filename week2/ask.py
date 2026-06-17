"""Week 2 — RAG Q&A CLI.

Embeds a question, retrieves the most relevant chunks from ChromaDB,
and generates a grounded answer with source citations.

Run from the repo root:
    python week2/ask.py "What is the return policy?"
    echo "What is the return policy?" | python week2/ask.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week1"))
import llm  # noqa: E402

import chromadb  # noqa: E402

CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".chromadb")
COLLECTION_NAME = "week2_docs"
TOP_K = 5

SYSTEM = (
    "You are a helpful assistant that answers questions using ONLY the provided context chunks. "
    "Follow these rules strictly:\n"
    "1. Answer based ONLY on the information in the context chunks below.\n"
    "2. Cite your sources using [source: filename] after each claim.\n"
    "3. If the context does not contain enough information to answer the question, "
    "respond with: \"I don't have enough information to answer that.\"\n"
    "4. Do not make up or infer information that is not explicitly stated in the context.\n"
    "5. If only part of the question can be answered, answer what you can and state "
    "what information is missing."
)


def build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"]["source"]
        parts.append(f"[Chunk {i} | source: {source}]\n{chunk['document']}")
    return "\n\n---\n\n".join(parts)


def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)
    query_embedding = llm.embed(question)[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return chunks


def ask(question: str, top_k: int = TOP_K, stream: bool = True) -> str:
    chunks = retrieve(question, top_k)
    context = build_context(chunks)

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Context:\n\n{context}\n\nQuestion: {question}"},
    ]

    model = llm.active_chat_model()
    input_tokens = llm.count_message_tokens(messages, model=model)

    if stream:
        print("answer> ", end="", flush=True)
        parts: list[str] = []
        for chunk in llm.chat(messages, stream=True):
            print(chunk, end="", flush=True)
            parts.append(chunk)
        answer = "".join(parts)
        output_tokens = llm.count_tokens(answer, model=model)
        print(f"\n\n[{llm.format_usage_estimate(input_tokens, output_tokens, model=model)}]")
    else:
        answer = llm.chat(messages)
        output_tokens = llm.count_tokens(answer, model=model)
        print(answer)
        print(f"\n[{llm.format_usage_estimate(input_tokens, output_tokens, model=model)}]")

    print("\nSources used:")
    seen = set()
    for c in chunks:
        src = c["metadata"]["source"]
        if src not in seen:
            seen.add(src)
            print(f"  - {src} (distance: {c['distance']:.4f})")

    return answer


def read_question() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    return sys.stdin.read().strip()


def main() -> None:
    question = read_question()
    if not question:
        print("No question provided. Pass as argument or pipe via stdin.", file=sys.stderr)
        sys.exit(1)
    ask(question)


if __name__ == "__main__":
    main()
