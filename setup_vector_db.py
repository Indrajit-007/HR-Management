"""Build the persisted Chroma vector store used by the RAG MCP server."""

from pathlib import Path
import os

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


SCRIPT_ROOT = Path(__file__).resolve().parent
load_dotenv(SCRIPT_ROOT / ".env")
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", str(SCRIPT_ROOT))).expanduser()


def configured_path(variable: str, default: str) -> Path:
    path = Path(os.getenv(variable, default)).expanduser()
    return (path if path.is_absolute() else PROJECT_ROOT / path).resolve()


POLICIES_DIR = configured_path("POLICIES_PATH", "data/policies")
ANNOUNCEMENTS_DIR = configured_path("ANNOUNCEMENTS_PATH", "data/announcements")
CHROMA_DIR = configured_path("CHROMA_DIR", "data/chroma_store")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents() -> list[Document]:
    documents: list[Document] = []

    for pdf_path in sorted(POLICIES_DIR.glob("*.pdf")):
        for document in PyPDFLoader(str(pdf_path)).load():
            document.metadata.update(
                source=pdf_path.name,
                type="policy",
                category=pdf_path.stem,
            )
            documents.append(document)

    for text_path in sorted(ANNOUNCEMENTS_DIR.glob("*.txt")):
        content = text_path.read_text(encoding="utf-8").strip()
        if content:
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": text_path.name,
                        "type": "announcement",
                        "category": "announcement",
                    },
                )
            )

    return documents


def main() -> None:
    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        raise FileExistsError(
            f"Chroma store already exists at {CHROMA_DIR}. "
            "Move or remove it before rebuilding to avoid mixing old and new data."
        )

    documents = load_documents()
    if not documents:
        raise RuntimeError(
            f"No PDFs found in {POLICIES_DIR} and no announcement text files found "
            f"in {ANNOUNCEMENTS_DIR}."
        )

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    policy_chunks = sum(chunk.metadata["type"] == "policy" for chunk in chunks)
    announcement_chunks = sum(
        chunk.metadata["type"] == "announcement" for chunk in chunks
    )
    print(f"Created Chroma store at: {CHROMA_DIR}")
    print(f"Indexed {policy_chunks} policy chunks and {announcement_chunks} announcement chunks.")


if __name__ == "__main__":
    main()
