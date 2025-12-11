"""Testes para o módulo de configuração."""

import os
import pytest
from pathlib import Path

from llm_rag.config import Config


def test_config_carrega_arquivo_yaml():
    """Testa se a configuração carrega o arquivo YAML corretamente."""
    config = Config()
    assert config.config_data is not None
    assert "chunking" in config.config_data
    assert "llm" in config.config_data


def test_config_propriedades_chunking():
    """Testa se as propriedades de chunking estão acessíveis."""
    config = Config()
    assert isinstance(config.chunk_size, int)
    assert isinstance(config.chunk_overlap, int)
    assert config.chunk_size > 0
    assert config.chunk_overlap >= 0


def test_config_propriedades_llm():
    """Testa se as propriedades do LLM estão acessíveis."""
    config = Config()
    assert isinstance(config.llm_temperatura, float)
    assert isinstance(config.llm_max_tokens, int)
    assert 0 <= config.llm_temperatura <= 2
    assert config.llm_max_tokens > 0


def test_config_propriedades_chromadb():
    """Testa se as propriedades do ChromaDB estão acessíveis."""
    config = Config()
    assert isinstance(config.chroma_host, str)
    assert isinstance(config.chroma_port, int)
    assert isinstance(config.chroma_colecao, str)


def test_config_propriedades_app():
    """Testa se as propriedades da aplicação estão acessíveis."""
    config = Config()
    assert isinstance(config.app_name, str)
    assert isinstance(config.app_version, str)
    assert len(config.app_name) > 0
    assert len(config.app_version) > 0
