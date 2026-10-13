"""MCP tools for semantic search over policy and announcement documents."""

import os
from pathlib import Path
from typing import Any

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv


SCRIPT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(SCRIPT_ROOT / ".env")
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", str(SCRIPT_ROOT))).expanduser()
mcp = FastMCP("RAGMCPServer")


class RAGMCPServer:
    """Semantic search over the project's persisted Chroma collection."""

    def __init__(self, chroma_dir: str | os.PathLike[str] | None = None):
        configured_dir = chroma_dir or os.getenv("CHROMA_DIR", "data/chroma_store")
        path = Path(configured_dir).expanduser()
        self.chroma_dir = (path if path.is_absolute() else PROJECT_ROOT / path).resolve()
        if not self.chroma_dir.is_dir():
            raise FileNotFoundError(
                f"Vector store not found: {self.chroma_dir}. Build the vector store first."
            )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Chroma(
            persist_directory=str(self.chroma_dir),
            embedding_function=self.embeddings,
        )

    def query_documents(
        self, query: str, top_k: int = 3, doc_type: str | None = None
    ) -> dict[str, Any]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20")

        search_options: dict[str, Any] = {"k": top_k}
        if doc_type:
            search_options["filter"] = {"type": doc_type}
        results = self.vectorstore.similarity_search(query, **search_options)
        formatted = [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "type": doc.metadata.get("type", "unknown"),
                "category": doc.metadata.get("category", "unknown"),
            }
            for doc in results
        ]
        return {
            "success": bool(formatted),
            "query": query,
            "results": formatted,
            "count": len(formatted),
            **({} if formatted else {"message": "No relevant documents found"}),
        }

    def query_policies(self, query: str, top_k: int = 3) -> dict[str, Any]:
        return self.query_documents(query, top_k, doc_type="policy")

    def query_announcements(self, query: str, top_k: int = 3) -> dict[str, Any]:
        return self.query_documents(query, top_k, doc_type="announcement")

    def get_policy_summary(self, policy_name: str) -> dict[str, Any]:
        if not policy_name.strip():
            raise ValueError("policy_name must not be empty")
        results = self.vectorstore.similarity_search(
            f"summary of {policy_name}", k=20, filter={"type": "policy"}
        )
        chunks = [
            doc for doc in results
            if policy_name.casefold() in doc.metadata.get("source", "").casefold()
        ]
        if not chunks:
            return {
                "success": False,
                "message": f"Policy '{policy_name}' not found",
                "summary": None,
            }
        return {
            "success": True,
            "policy_name": policy_name,
            "summary": "\n\n".join(doc.page_content for doc in chunks[:3]),
            "source": chunks[0].metadata.get("source", "unknown"),
        }

    def list_policies(self) -> dict[str, Any]:
        stored = self.vectorstore.get(where={"type": "policy"}, include=["metadatas"])
        sources = sorted({
            metadata.get("source", "unknown")
            for metadata in (stored.get("metadatas") or [])
        })
        return {"policies": sources, "count": len(sources)}


_server: RAGMCPServer | None = None


def _rag() -> RAGMCPServer:
    global _server
    if _server is None:
        _server = RAGMCPServer()
    return _server


@mcp.tool()
def query_documents(query: str, top_k: int = 3, doc_type: str | None = None) -> dict[str, Any]:
    """Search indexed documents, optionally limited to policy or announcement."""
    if doc_type not in (None, "policy", "announcement"):
        raise ValueError("doc_type must be 'policy', 'announcement', or omitted")
    return _rag().query_documents(query, top_k, doc_type)


@mcp.tool()
def query_policies(query: str, top_k: int = 3) -> dict[str, Any]:
    """Search indexed HR policy documents."""
    return _rag().query_policies(query, top_k)


@mcp.tool()
def query_announcements(query: str, top_k: int = 3) -> dict[str, Any]:
    """Search indexed announcement documents."""
    return _rag().query_announcements(query, top_k)


@mcp.tool()
def get_policy_summary(policy_name: str) -> dict[str, Any]:
    """Retrieve the most relevant indexed sections for a named policy."""
    return _rag().get_policy_summary(policy_name)


@mcp.tool()
def list_policies() -> dict[str, Any]:
    """List distinct policy source names stored in the vector database."""
    return _rag().list_policies()


if __name__ == "__main__":
    mcp.run(transport="stdio")
