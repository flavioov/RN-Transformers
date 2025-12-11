"""Testes para o módulo de embeddings."""

import pytest

from llm_rag.embeddings import EmbeddingManager


def test_embedding_manager_inicializacao():
    """Testa se o gerenciador de embeddings é inicializado corretamente."""
    manager = EmbeddingManager()
    assert manager is not None
    assert manager.embedding_model is not None


def test_embedding_manager_embed_query():
    """Testa se o embedding de consulta é gerado corretamente."""
    manager = EmbeddingManager()
    texto = "Esta é uma consulta de teste"

    embedding = manager.embed_query(texto)

    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_embedding_manager_embed_documents():
    """Testa se embeddings de documentos são gerados corretamente."""
    manager = EmbeddingManager()
    textos = [
        "Primeiro documento de teste",
        "Segundo documento de teste",
        "Terceiro documento de teste",
    ]

    embeddings = manager.embed_documents(textos)

    assert embeddings is not None
    assert isinstance(embeddings, list)
    assert len(embeddings) == 3
    assert all(isinstance(emb, list) for emb in embeddings)


def test_embedding_manager_dimension():
    """Testa se a dimensão do embedding é retornada corretamente."""
    manager = EmbeddingManager()
    dimension = manager.dimension

    assert isinstance(dimension, int)
    assert dimension > 0
