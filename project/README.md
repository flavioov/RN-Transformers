# llm-rag

A demonstration application showcasing RAG (Retrieval-Augmented Generation) with Large Language Models.

## Overview

This project demonstrates how to build an LLM application enhanced with RAG capabilities. It uses **ChromaDB** as a vector store to enable semantic search and context retrieval, allowing the LLM to provide more accurate and contextually relevant responses based on stored documents.

### Key Components

- **LLM Integration**: Language model integration for natural language understanding and generation
- **RAG Pipeline**: Retrieval-Augmented Generation for context-aware responses
- **ChromaDB**: High-performance vector database for semantic search and document storage
- **Vector Embeddings**: Document embeddings for similarity-based retrieval

## Features

- Poetry for dependency management
- Pre-commit hooks for code quality (ruff, pydocstyle)
- Google-style docstrings
- 88 character line length
- Source code in `src/llm_rag/`
- ChromaDB vector store integration

## Installation

```bash
# Install dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install
```

## Development

```bash
# Run pre-commit checks
poetry run pre-commit run --all-files

# Run ruff check
poetry run ruff check .

# Run ruff format
poetry run ruff format .
```

## Project Structure

```
project/
├── src/llm_rag/       # Main package source code
├── tests/             # Test files
└── pyproject.toml     # Project configuration
```
