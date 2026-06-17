"""Week 2 — Document ingestion pipeline.

Loads documents from a directory, chunks them, embeds via llm.embed(),
and persists to a local ChromaDB collection.

Run from the repo root:
    python week2/ingest.py                   # ingest week2/docs/
    python week2/ingest.py /path/to/docs/    # ingest a custom directory
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week1"))
import llm  # noqa: E402

import chromadb  # noqa: E402
from pypdf import PdfReader  # noqa: E402

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".chromadb")
COLLECTION_NAME = "week2_docs"


def load_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text.strip()] if text.strip() else []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


def load_documents(docs_dir: str) -> list[dict]:
    docs_path = Path(docs_dir)
    if not docs_path.is_dir():
        print(f"Error: {docs_dir} is not a directory.", file=sys.stderr)
        sys.exit(1)

    documents = []
    for path in sorted(docs_path.iterdir()):
        if path.suffix.lower() in (".md", ".txt", ".pdf"):
            text = load_file(path)
            if text.strip():
                documents.append({"filename": path.name, "text": text})
                print(f"  loaded {path.name} ({len(text)} chars)")
    return documents


def main() -> None:
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "docs"
    )

    print(f"Loading documents from {docs_dir} ...")
    documents = load_documents(docs_dir)
    if not documents:
        print("No documents found.", file=sys.stderr)
        sys.exit(1)

    all_chunks = []
    all_ids = []
    all_metadata = []
    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['filename']}::chunk_{i}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadata.append({"source": doc["filename"], "chunk_index": i})
        print(f"  chunked {doc['filename']} -> {len(chunks)} chunks")

    print(f"\nEmbedding {len(all_chunks)} chunks ...")
    embeddings = llm.embed(all_chunks)
    print(f"  got {len(embeddings)} embeddings (dim={len(embeddings[0])})")

    print(f"\nPersisting to ChromaDB at {CHROMA_DIR} ...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    collection.upsert(
        ids=all_ids,
        embeddings=embeddings,
        documents=all_chunks,
        metadatas=all_metadata,
    )
    print(f"  collection '{COLLECTION_NAME}' now has {collection.count()} chunks")
    print("\nDone.")


if __name__ == "__main__":
    main()
