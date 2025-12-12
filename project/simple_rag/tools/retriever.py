"""Ferramenta de recuperação de documentos."""

from langchain.tools import tool

from simple_rag.utils.logger import setup_logger
from simple_rag.utils.vectorstore import get_vectorstore

logger = setup_logger(__name__)
vectorstore = get_vectorstore()


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retriever to search for private information in a vectorstore."""
    logger.info(f"🔍 Vectorstore READ: Searching for query: '{query[:100]}...'")
    retrieved_docs = vectorstore.similarity_search(query, k=4)
    logger.info(
        f"✓ Vectorstore READ completed: Retrieved {len(retrieved_docs)} document(s)"
    )
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in retrieved_docs
    )
    return serialized, retrieved_docs
