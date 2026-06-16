"""Week 1 — structured-data extractor.

Demonstrates: OpenAI structured outputs + Pydantic to turn messy free text into
a validated, typed object — far more reliable than prompting "return JSON".

Run from the repo root:
    echo "Jane Doe, jane@co.com, wants the Enterprise plan, asked for a demo" | python week1/extract.py
    python week1/extract.py path/to/text.txt

Stretch goals:
    - Add fields (phone, job title) and see how extraction adapts.
    - Feed 10 messy inputs and confirm you never get a parse error.
    - Swap the model to gpt-4.1-mini and compare quality vs. cost.
"""

# NOTE: intentionally no `from __future__ import annotations` here — it makes
# Pydantic defer schema building and can fail to resolve `Optional`. Evaluating
# annotations eagerly keeps the Pydantic model robust however it's imported.

import os
import sys
from typing import Optional

# Allow `import llm` whether you run this from the repo root or week1/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm  # noqa: E402

from pydantic import BaseModel, Field  # noqa: E402


class Contact(BaseModel):
    """The shape we want to pull out of the text. Optional fields stay null
    when absent — the prompt tells the model not to guess."""

    name: Optional[str] = Field(None, description="Person's full name")
    email: Optional[str] = Field(None, description="Email address")
    company: Optional[str] = Field(None, description="Company name, if mentioned")
    plan: Optional[str] = Field(None, description="Plan or product of interest")
    demo_requested: bool = Field(False, description="True if they asked for a demo")


SYSTEM = (
    "Extract contact details from the text into the given schema. "
    "If a field is not present, leave it null — do not guess or invent values."
)


def read_input() -> str:
    """Read from a file path arg if given, otherwise from stdin."""
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def main() -> None:
    text = read_input().strip()
    if not text:
        print("No input. Pipe text in or pass a file path.", file=sys.stderr)
        sys.exit(1)

    contact = llm.parse(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
        response_format=Contact,
    )
    print(contact.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
