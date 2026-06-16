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
    role: Optional[str] = Field(None, description="Role of the person")
    company: Optional[str] = Field(None, description="Company name, if mentioned")
    plan: Optional[str] = Field(None, description="Plan or product of interest")
    demo_requested: bool = Field(False, description="True if they asked for a demo")


SYSTEM = (
    "Extract contact details from the text into the given schema. "
    "If a field is not present, leave it null — do not guess or invent values. "
    "Set demo_requested to true when the text asks for a demo, showing, "
    "walkthrough, product tour, or to be shown the product. "
    "Keep it false when the text explicitly says no demo is needed."
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

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": text},
    ]
    model = llm.active_chat_model()
    input_tokens = llm.count_message_tokens(messages, model=model)

    contact = llm.parse(
        messages=messages,
        response_format=Contact,
        model=model,
    )
    output_json = contact.model_dump_json(indent=2)
    output_tokens = llm.count_tokens(output_json, model=model)
    print(output_json)
    print(
        f"[{llm.format_usage_estimate(input_tokens, output_tokens, model=model)}]",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
