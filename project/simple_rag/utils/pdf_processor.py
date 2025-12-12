"""PDF processing utilities for document upload and indexing."""

import asyncio
from typing import Callable

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from simple_rag.utils.logger import setup_logger

logger = setup_logger(__name__)


def _process_single_pdf(uploaded_file, vectorstore) -> tuple[int, str | None]:
    """Process a single PDF file synchronously (runs in thread pool).

    Args:
        uploaded_file: Chainlit File object with PDF content
        vectorstore: ChromaDB vectorstore instance to add documents to

    Returns:
        Tuple of (chunks_added, error_message_or_None)
    """
    try:
        logger.info(f"Processing file: {uploaded_file.name}")

        # Load PDF
        loader = PyPDFLoader(uploaded_file.path)
        documents = loader.load()

        if not documents:
            error_msg = (
                f"{uploaded_file.name}: PDF is empty or contains no extractable text"
            )
            logger.warning(error_msg)
            return 0, error_msg

        logger.info(f"Extracted {len(documents)} page(s) from {uploaded_file.name}")

        # Add source filename to metadata
        for doc in documents:
            doc.metadata["source_file"] = uploaded_file.name

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        chunks = text_splitter.split_documents(documents)

        logger.info(f"Split {uploaded_file.name} into {len(chunks)} chunk(s)")

        # Add chunks to vectorstore
        vectorstore.add_documents(documents=chunks)

        logger.info(
            f"Successfully indexed {uploaded_file.name}: {len(chunks)} chunks added"
        )

        return len(chunks), None

    except Exception as e:
        error_msg = f"{uploaded_file.name}: {e!s}"
        logger.error(f"Error processing {uploaded_file.name}: {e}", exc_info=True)
        return 0, error_msg


async def process_pdf_files(
    uploaded_files: list,
    vectorstore,
    progress_callback: Callable[[str], None] | None = None,
) -> tuple[int, list[str]]:
    """Process uploaded PDF files asynchronously and add to vectorstore.

    Args:
        uploaded_files: List of Chainlit File objects with PDF content
        vectorstore: ChromaDB vectorstore instance to add documents to
        progress_callback: Optional async callback function to report progress

    Returns:
        Tuple of (total_chunks_added, list_of_error_messages)
    """
    total_chunks = 0
    errors = []

    logger.info(f"Processing {len(uploaded_files)} PDF file(s)...")

    for idx, uploaded_file in enumerate(uploaded_files, 1):
        # Update progress
        if progress_callback:
            await progress_callback(
                f"📄 Processing file {idx}/{len(uploaded_files)}: {uploaded_file.name}..."
            )

        # Run the blocking PDF processing in a thread pool
        chunks_added, error = await asyncio.to_thread(
            _process_single_pdf, uploaded_file, vectorstore
        )

        total_chunks += chunks_added
        if error:
            errors.append(error)

    logger.info(
        f"PDF processing complete: {total_chunks} total chunks added, {len(errors)} errors"
    )

    return total_chunks, errors
