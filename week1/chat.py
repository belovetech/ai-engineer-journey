"""Week 1 — streaming multi-turn CLI chatbot.

Demonstrates: multi-turn state (the API is stateless, so we resend history),
streaming output, and routing every call through the llm.py abstraction.

Run from the repo root:
    python week1/chat.py

Commands:
    /reset   clear the conversation history
    /exit    quit (Ctrl-D / Ctrl-C also work)
"""

from __future__ import annotations

import os
import sys

# Allow `import llm` whether you run this from the repo root or week1/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm  # noqa: E402

SYSTEM_PROMPT = "You are a concise, helpful assistant. Prefer clear, direct answers."


class ConversationManager:
    """Holds the running message history for a multi-turn conversation."""

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.reset()

    def reset(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})


def main() -> None:
    convo = ConversationManager(SYSTEM_PROMPT)
    print("Chat ready. Type /reset to clear history, /exit to quit.\n")

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user:
            continue
        if user == "/exit":
            break
        if user == "/reset":
            convo.reset()
            print("(history cleared)\n")
            continue

        convo.add_user(user)
        model = llm.active_chat_model()
        input_tokens = llm.count_message_tokens(convo.messages, model=model)

        # Stream the reply token-by-token, collecting it for the history.
        print("ai>  ", end="", flush=True)
        parts: list[str] = []
        for chunk in llm.chat(convo.messages, model=model, stream=True):
            print(chunk, end="", flush=True)
            parts.append(chunk)
        assistant_text = "".join(parts)
        output_tokens = llm.count_tokens(assistant_text, model=model)
        print(f"\n\n[{llm.format_usage_estimate(input_tokens, output_tokens, model=model)}]\n")
        convo.add_assistant(assistant_text)


if __name__ == "__main__":
    main()
