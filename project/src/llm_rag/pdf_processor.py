"""Módulo para processamento e extração de texto de arquivos PDF.

Este módulo fornece funcionalidades para extrair texto de PDFs e dividir
em chunks apropriados para indexação.
"""

import hashlib
from pathlib import Path
from typing import List, Dict, Any

import pymupdf  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter

from llm_rag.config import config


class DocumentChunk:
    """Representa um chunk de documento com metadados."""

    def __init__(
        self,
        texto: str,
        metadata: Dict[str, Any],
        chunk_id: str,
    ):
        """Inicializa um chunk de documento.

        Args:
            texto: Conteúdo textual do chunk.
            metadata: Metadados do chunk (página, documento, etc.).
            chunk_id: Identificador único do chunk.
        """
        self.texto = texto
        self.metadata = metadata
        self.chunk_id = chunk_id

    def to_dict(self) -> Dict[str, Any]:
        """Converte o chunk para dicionário.

        Returns:
            Dicionário com os dados do chunk.
        """
        return {
            "texto": self.texto,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id,
        }


class PDFProcessor:
    """Processador de arquivos PDF."""

    def __init__(self):
        """Inicializa o processador de PDF."""
        self.text_splitter = self._criar_text_splitter()

    def _criar_text_splitter(self):
        """Cria o divisor de texto baseado na configuração.

        Returns:
            Instância do divisor de texto.
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def extrair_texto_pdf(self, caminho_pdf: Path) -> List[Dict[str, Any]]:
        """Extrai texto de um arquivo PDF página por página.

        Args:
            caminho_pdf: Caminho para o arquivo PDF.

        Returns:
            Lista de dicionários contendo texto e número da página.

        Raises:
            FileNotFoundError: Se o arquivo não for encontrado.
            ValueError: Se o arquivo não for um PDF válido.
        """
        if not caminho_pdf.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")

        if caminho_pdf.suffix.lower() != ".pdf":
            raise ValueError(f"Arquivo não é um PDF: {caminho_pdf}")

        paginas = []

        try:
            # Abrir o PDF
            documento = pymupdf.open(caminho_pdf)

            # Extrair texto de cada página
            for num_pagina, pagina in enumerate(documento, start=1):
                texto = pagina.get_text()

                # Pular páginas vazias
                if texto.strip():
                    paginas.append(
                        {
                            "texto": texto,
                            "numero_pagina": num_pagina,
                            "total_paginas": len(documento),
                        }
                    )

            documento.close()

        except Exception as e:
            raise ValueError(f"Erro ao processar PDF: {str(e)}")

        return paginas

    def _gerar_chunk_id(self, texto: str, documento_nome: str, indice: int) -> str:
        """Gera um ID único para um chunk.

        Args:
            texto: Conteúdo do chunk.
            documento_nome: Nome do documento.
            indice: Índice do chunk no documento.

        Returns:
            ID único do chunk.
        """
        # Usar hash do conteúdo + nome do documento + índice
        conteudo = f"{documento_nome}_{indice}_{texto[:100]}"
        return hashlib.md5(conteudo.encode()).hexdigest()

    def processar_pdf(
        self, caminho_pdf: Path, documento_id: str = None
    ) -> List[DocumentChunk]:
        """Processa um PDF completo e retorna chunks indexáveis.

        Args:
            caminho_pdf: Caminho para o arquivo PDF.
            documento_id: ID personalizado do documento (opcional).

        Returns:
            Lista de chunks de documento prontos para indexação.
        """
        # Extrair texto do PDF
        paginas = self.extrair_texto_pdf(caminho_pdf)

        # Usar nome do arquivo como ID se não fornecido
        if documento_id is None:
            documento_id = caminho_pdf.stem

        chunks = []
        chunk_index = 0

        # Processar cada página
        for pagina_info in paginas:
            texto = pagina_info["texto"]
            num_pagina = pagina_info["numero_pagina"]

            # Dividir texto em chunks
            texto_chunks = self.text_splitter.split_text(texto)

            # Criar objetos DocumentChunk
            for texto_chunk in texto_chunks:
                chunk_id = self._gerar_chunk_id(
                    texto_chunk, documento_id, chunk_index
                )

                metadata = {
                    "documento_id": documento_id,
                    "documento_nome": caminho_pdf.name,
                    "numero_pagina": num_pagina,
                    "total_paginas": pagina_info["total_paginas"],
                    "chunk_index": chunk_index,
                    "caminho_arquivo": str(caminho_pdf),
                }

                chunk = DocumentChunk(
                    texto=texto_chunk,
                    metadata=metadata,
                    chunk_id=chunk_id,
                )

                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def obter_info_pdf(self, caminho_pdf: Path) -> Dict[str, Any]:
        """Obtém informações básicas sobre um PDF.

        Args:
            caminho_pdf: Caminho para o arquivo PDF.

        Returns:
            Dicionário com informações do PDF.
        """
        if not caminho_pdf.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")

        documento = pymupdf.open(caminho_pdf)

        info = {
            "nome": caminho_pdf.name,
            "total_paginas": len(documento),
            "tamanho_bytes": caminho_pdf.stat().st_size,
            "tamanho_mb": round(caminho_pdf.stat().st_size / (1024 * 1024), 2),
            "metadata": documento.metadata,
        }

        documento.close()

        return info


# Instância global do processador de PDF
pdf_processor = PDFProcessor()
