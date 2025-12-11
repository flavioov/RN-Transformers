"""Testes para o módulo de processamento de PDF."""

import pytest
from pathlib import Path

from llm_rag.pdf_processor import PDFProcessor, DocumentChunk


def test_pdf_processor_inicializacao():
    """Testa se o processador de PDF é inicializado corretamente."""
    processor = PDFProcessor()
    assert processor is not None
    assert processor.text_splitter is not None


def test_document_chunk_to_dict():
    """Testa se DocumentChunk converte para dicionário corretamente."""
    chunk = DocumentChunk(
        texto="Texto de teste",
        metadata={"documento_id": "test", "numero_pagina": 1},
        chunk_id="test123",
    )

    chunk_dict = chunk.to_dict()
    assert chunk_dict["texto"] == "Texto de teste"
    assert chunk_dict["metadata"]["documento_id"] == "test"
    assert chunk_dict["chunk_id"] == "test123"


def test_pdf_processor_extrair_texto_arquivo_inexistente():
    """Testa se FileNotFoundError é lançado para arquivo inexistente."""
    processor = PDFProcessor()
    caminho_inexistente = Path("/caminho/inexistente/arquivo.pdf")

    with pytest.raises(FileNotFoundError):
        processor.extrair_texto_pdf(caminho_inexistente)


def test_pdf_processor_arquivo_nao_pdf():
    """Testa se ValueError é lançado para arquivo não-PDF."""
    processor = PDFProcessor()
    caminho_txt = Path("/tmp/teste.txt")

    # Criar arquivo temporário
    caminho_txt.touch()

    try:
        with pytest.raises(ValueError, match="não é um PDF"):
            processor.extrair_texto_pdf(caminho_txt)
    finally:
        caminho_txt.unlink()


def test_pdf_processor_gerar_chunk_id():
    """Testa se chunk IDs são gerados corretamente."""
    processor = PDFProcessor()

    chunk_id_1 = processor._gerar_chunk_id("texto teste", "doc1", 0)
    chunk_id_2 = processor._gerar_chunk_id("texto teste", "doc1", 0)
    chunk_id_3 = processor._gerar_chunk_id("texto diferente", "doc1", 0)

    # Mesmo conteúdo deve gerar mesmo ID
    assert chunk_id_1 == chunk_id_2

    # Conteúdo diferente deve gerar ID diferente
    assert chunk_id_1 != chunk_id_3
