"""Interactive CLI for the RAG agent.

Run: python cli.py   (from rag_agent_demo/)
"""
from __future__ import annotations

from src.agent import RagAgent

SESSION_ID = "cli-default"

BANNER = """
================================================================
 RockBot Agentic RAG — CLI
   Type your question and press Enter.
   Commands:  /reset  — clear chat history
              /quit   — exit
================================================================
""".strip()


def main() -> None:
    print(BANNER)
    agent = RagAgent()

    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            return

        if not question:
            continue
        if question == "/quit":
            print("bye.")
            return
        if question == "/reset":
            agent.reset(SESSION_ID)
            print("(history cleared)")
            continue

        try:
            answer = agent.ask(question, session_id=SESSION_ID)
        except Exception as e:
            print(f"[error] {e}")
            continue

        print(f"\n{answer}")


if __name__ == "__main__":
    main()
