"""Agentic RAG agent using Claude + LangChain tool-calling."""
from __future__ import annotations

from typing import Optional

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import config
from src.tools import ALL_TOOLS

SYSTEM_PROMPT = """You are RockBot Assistant, an Agentic RAG assistant.

You have access to four tools:
  1. search_documents — internal product/FAQ documents
  2. query_database   — read-only SQL over employees / sales tables
  3. search_web       — Tavily web search for fresh / external info
  4. calculate        — arithmetic

Guidelines:
- Always pick the most appropriate tool. You may call multiple tools in sequence.
- For company/product questions → search_documents.
- For employee or revenue numbers → query_database.
- For news / external / time-sensitive info → search_web.
- For any non-trivial arithmetic → calculate (do NOT compute in your head).
- If a tool returns an error or no results, try a different approach or tool.
- Cite the data source when relevant (file name or table name).
- Reply in the SAME language as the user's question.
"""


def _build_executor(memory: ConversationBufferMemory) -> AgentExecutor:
    config.require_anthropic_key()

    llm = ChatAnthropic(
        model=config.CLAUDE_MODEL,
        api_key=config.ANTHROPIC_API_KEY,
        base_url=config.ANTHROPIC_BASE_URL or None,
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=8,
    )


class RagAgent:
    """Multi-session Agentic RAG.

    A single session_id keeps its own ConversationBufferMemory so multi-turn
    follow-ups work. session_id=None means stateless (fresh memory per call).
    """

    def __init__(self) -> None:
        self._sessions: dict[str, AgentExecutor] = {}

    def _get_executor(self, session_id: Optional[str]) -> AgentExecutor:
        if session_id is None:
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
            return _build_executor(memory)

        if session_id not in self._sessions:
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
            self._sessions[session_id] = _build_executor(memory)
        return self._sessions[session_id]

    def ask(self, question: str, session_id: Optional[str] = None) -> str:
        executor = self._get_executor(session_id)
        result = executor.invoke({"input": question})
        output = result.get("output", "")
        if isinstance(output, list):
            output = "".join(
                block.get("text", "")
                for block in output
                if isinstance(block, dict) and block.get("type") == "text"
            )
        return output

    def reset(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
