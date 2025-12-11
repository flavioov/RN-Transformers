# Claude Context: LLM RAG Project

## Project Overview

**llm-rag** is a demonstration application that showcases RAG (Retrieval-Augmented Generation) capabilities with Large Language Models. The project is configured with Poetry for dependency management and pre-commit hooks for code quality enforcement.

### Purpose

This is a **demonstration/proof-of-concept** application designed to illustrate how to:
- Integrate an LLM with a vector database for enhanced context retrieval
- Implement RAG patterns for more accurate and contextually relevant responses
- Use ChromaDB as a vector store for semantic search
- Build a complete LLM application with retrieval capabilities

### Architecture

The application uses the following architecture:

1. **Vector Store**: ChromaDB for storing and retrieving document embeddings
2. **Embeddings**: Vector representations of documents for similarity search
3. **RAG Pipeline**: Retrieves relevant context from ChromaDB before LLM inference
4. **LLM Integration**: Language model that uses retrieved context to generate responses

### Key Technologies

- **ChromaDB**: Vector database for semantic search and document storage
- **LLM**: Large Language Model for natural language understanding and generation
- **Vector Embeddings**: For similarity-based document retrieval
- **RAG Pattern**: Retrieval-Augmented Generation for context-aware responses

## Project Structure

```
project/
├── src/
│   └── llm_rag/            # Main package (note: underscores, not hyphens)
│       └── __init__.py     # Package initialization
├── tests/                  # Test directory
│   └── __init__.py
├── pyproject.toml          # Poetry configuration and tool settings
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── poetry.lock             # Locked dependencies
├── README.md               # Project documentation
└── CLAUDE.md              # This file - AI assistant context
```

**Important**: The package name is `llm-rag` (with hyphen) in PyPI/Poetry, but the Python module is `llm_rag` (with underscore) following Python naming conventions.

## Development Tools & Configuration

### Poetry
- **Purpose**: Dependency management and packaging
- **Package Name**: llm-rag
- **Module Name**: llm_rag (importable as `import llm_rag`)
- **Python Version**: ^3.8
- **Package Location**: `src/llm_rag/`
- **Install dependencies**: `poetry install --with dev`
- **Run commands**: `poetry run <command>`

### Pre-commit Hooks
Automatically run on git commits to enforce code quality:

1. **Ruff Check**: Linting with auto-fix enabled
2. **Ruff Format**: Code formatting
3. **Pydocstyle**: Docstring style checking

**Manual execution**: `poetry run pre-commit run --all-files`

### Code Style Standards

#### Ruff Configuration
- **Line length**: 88 characters
- **Target Python**: 3.8+
- **Enabled checks**:
  - E/F/W: pycodestyle errors, pyflakes, warnings
  - I: isort (import sorting)
  - N: pep8-naming
  - D: pydocstyle (docstring checks)
- **Quote style**: Double quotes
- **Indent style**: Spaces

#### Docstring Convention
- **Style**: Google style
- **Configuration**: pyproject.toml lines 35, 38

## Working with This Project

### Initial Setup
```bash
# Navigate to project directory
cd /home/flavio/github/RN-Transformers/project

# Install dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install
```

### Development Workflow
1. Make code changes following the style guide (88 char line length, Google docstrings)
2. Pre-commit hooks will automatically run on `git commit`
3. If hooks fail, fix issues and commit again
4. Manually check all files: `poetry run pre-commit run --all-files`

### Adding New Dependencies
```bash
# Production dependency
poetry add <package-name>

# Development dependency
poetry add --group dev <package-name>
```

### Running Code Quality Checks Manually
```bash
# Run all pre-commit hooks
poetry run pre-commit run --all-files

# Run ruff check only
poetry run ruff check .

# Run ruff format only
poetry run ruff format .

# Run pydocstyle only
poetry run pydocstyle .
```

## Important Notes for AI Assistants

1. **Always follow Google docstring convention** when writing or modifying functions/classes
2. **Maintain 88 character line length** for all Python code
3. **Run pre-commit hooks** after making changes to ensure code quality
4. **Add type hints** to function signatures when possible
5. **Keep imports sorted** (handled automatically by ruff)
6. **Use double quotes** for strings (handled automatically by ruff format)

## Configuration Files Reference

- **pyproject.toml**: Lines 21-39 contain tool configurations
  - Ruff: Lines 21-35
  - Pydocstyle: Lines 37-39
- **.pre-commit-config.yaml**: Pre-commit hook definitions

## Troubleshooting

### Pre-commit hook failures
- Check the error message for specific violations
- Run `poetry run ruff check . --fix` to auto-fix many issues
- Run `poetry run ruff format .` to format code
- Manually fix docstring issues identified by pydocstyle

### Poetry issues
- Update lock file: `poetry lock --no-update`
- Clear cache: `poetry cache clear --all pypi`
- Reinstall: `poetry install --with dev --sync`
