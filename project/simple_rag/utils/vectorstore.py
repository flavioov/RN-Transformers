from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from simple_rag.utils.logger import setup_logger
from simple_rag.config.config import settings

logger = setup_logger(__name__)


def _load_documents(directory: str = "./data/anamnese") -> list:
    documents = []

    for file in Path(directory).glob("*.txt"):
        documents.extend(TextLoader(file).load())

    return documents


def split_documents(documents: list) -> list:
    """Split documents into chunks using consistent parameters.

    This function is used for both initial .txt loading and PDF uploads.

    Args:
        documents: List of documents to split into chunks.

    Returns:
        List of document chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    logger.info(
        "Splitting documents into chunks... chunk_size=1000 and chunk_overlap=200"
    )
    return text_splitter.split_documents(documents)


def _split_documents(documents: list) -> list:
    """Divide os documentos em chunks."""
    return split_documents(documents)


def get_ollama_embedding_function(model: str = "llama3"):
    """Get Ollama embedding function.

    Args:
        model: Name of the Ollama model to use for embeddings.

    Returns:
        OllamaEmbeddings instance.
    """
    logger.info(f"Loading Ollama embedding model: {model}")
    return OllamaEmbeddings(model=settings.embedding_model)


def get_vectorstore(
    collection_name: str = "my_collection",
) -> Chroma:
    """Get or create a ChromaDB vector store.

    Args:
        collection_name: Name of the collection to use.

    Returns:
        Chroma vector store instance.
    """
    vector_store = Chroma(
        collection_name="my_collection",
        embedding_function=get_ollama_embedding_function(),
        host="localhost",
        port="9001"
    )
    # _load_vectorstore(vector_store)
    return vector_store


def load_vectorstore(vector_store: Chroma):
    logger.info("Loading documents into vectorstore...")
    all_splits = _split_documents(_load_documents())
    vector_store.add_documents(documents=all_splits)
    logger.info("Vectorstore loaded.")


if __name__ == "__main__":
    vector_store = get_vectorstore()
    response = vector_store.similarity_search("Identificação")
    print(response)
