"""Módulo para gerenciamento de modelos de embedding.

Este módulo fornece uma interface unificada para trabalhar com diferentes
modelos de embedding de texto.
"""

from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from llm_rag.config import config


class EmbeddingManager:
    """Gerenciador de modelos de embedding."""

    def __init__(self):
        """Inicializa o gerenciador de embeddings."""
        self.embedding_model = self._criar_embedding_model()

    def _criar_embedding_model(self):
        """Cria o modelo de embedding baseado na configuração.

        Returns:
            Instância do modelo de embedding.
        """
        model_name = config.embedding_model

        # Se for um modelo OpenAI
        if "openai" in model_name.lower() or "text-embedding" in model_name.lower():
            if not config.openai_api_key:
                raise ValueError("OPENAI_API_KEY necessária para embeddings OpenAI")
            return OpenAIEmbeddings(
                model=model_name,
                openai_api_key=config.openai_api_key,
            )

        # Caso contrário, usar HuggingFace (inclui sentence-transformers)
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de documentos.

        Args:
            texts: Lista de textos para gerar embeddings.

        Returns:
            Lista de vetores de embedding.
        """
        return self.embedding_model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Gera embedding para uma consulta.

        Args:
            text: Texto da consulta.

        Returns:
            Vetor de embedding da consulta.
        """
        return self.embedding_model.embed_query(text)

    @property
    def dimension(self) -> int:
        """Retorna a dimensão dos vetores de embedding.

        Returns:
            Dimensão do vetor de embedding.
        """
        # Testar com um texto de exemplo
        sample_embedding = self.embed_query("teste")
        return len(sample_embedding)


# Instância global do gerenciador de embeddings
embedding_manager = EmbeddingManager()
