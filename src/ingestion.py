"""Document ingestion: read docs, split, embed, persist into ChromaDB.

Run: python -m src.ingestion   (from rag_agent_demo/)
"""
from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import config


def _load_docs(docs_dir: str) -> list[Document]:
    docs: list[Document] = []
    for path in Path(docs_dir).rglob("*"):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs


def _split(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )
    return splitter.split_documents(docs)


def build_vectorstore() -> Chroma:
    """Build (or rebuild) the ChromaDB vectorstore from DOCS_DIR."""
    raw_docs = _load_docs(config.DOCS_DIR)
    if not raw_docs:
        raise RuntimeError(f"No .md/.txt files found under {config.DOCS_DIR}")

    chunks = _split(raw_docs)
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

    vs = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=config.CHROMA_COLLECTION,
        persist_directory=config.CHROMA_PERSIST_DIR,
    )
    print(
        f"Ingested {len(raw_docs)} files → {len(chunks)} chunks "
        f"into {config.CHROMA_PERSIST_DIR}"
    )
    return vs


def get_vectorstore() -> Chroma:
    """Open an existing vectorstore (read-only use case)."""
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    return Chroma(
        collection_name=config.CHROMA_COLLECTION,
        embedding_function=embeddings,
        persist_directory=config.CHROMA_PERSIST_DIR,
    )


if __name__ == "__main__":
    build_vectorstore()
