"""Módulo principal do agente RAG.

Este módulo fornece a interface de alto nível para interagir com o agente.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

from llm_rag.config import config
from llm_rag.pdf_processor import pdf_processor
from llm_rag.vector_store import vector_store
from llm_rag.graph.workflow import rag_workflow
from llm_rag.graph.state import AgentState


class DocumentManager:
    """Gerenciador de documentos para o agente RAG."""

    def __init__(self):
        """Inicializa o gerenciador de documentos."""
        # Criar diretório de uploads se não existir
        self.upload_dir = Path(config.upload_directory)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Inicializar coleção ChromaDB
        vector_store.criar_colecao()

    def indexar_pdf(self, caminho_pdf: Path, documento_id: Optional[str] = None) -> Dict[str, Any]:
        """Indexa um arquivo PDF no vector store.

        Args:
            caminho_pdf: Caminho para o arquivo PDF.
            documento_id: ID personalizado do documento.

        Returns:
            Dicionário com informações sobre a indexação.
        """
        # Validar arquivo
        if not caminho_pdf.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")

        # Obter informações do PDF
        info_pdf = pdf_processor.obter_info_pdf(caminho_pdf)

        # Validar tamanho
        if info_pdf["tamanho_mb"] > config.upload_max_size_mb:
            raise ValueError(
                f"Arquivo muito grande: {info_pdf['tamanho_mb']}MB. "
                f"Máximo permitido: {config.upload_max_size_mb}MB"
            )

        # Processar PDF em chunks
        chunks = pdf_processor.processar_pdf(caminho_pdf, documento_id)

        # Adicionar ao vector store
        num_chunks = vector_store.adicionar_documentos(chunks)

        return {
            "documento_id": documento_id or caminho_pdf.stem,
            "documento_nome": caminho_pdf.name,
            "total_paginas": info_pdf["total_paginas"],
            "tamanho_mb": info_pdf["tamanho_mb"],
            "num_chunks": num_chunks,
            "sucesso": True,
        }

    def listar_documentos(self) -> List[Dict[str, Any]]:
        """Lista todos os documentos indexados.

        Returns:
            Lista de documentos com informações básicas.
        """
        return vector_store.listar_documentos()

    def deletar_documento(self, documento_id: str) -> Dict[str, Any]:
        """Deleta um documento do vector store.

        Args:
            documento_id: ID do documento a deletar.

        Returns:
            Dicionário com resultado da operação.
        """
        num_deletado = vector_store.deletar_documento(documento_id)

        return {
            "documento_id": documento_id,
            "chunks_deletados": num_deletado,
            "sucesso": num_deletado > 0,
        }

    def limpar_todos_documentos(self):
        """Remove todos os documentos indexados."""
        vector_store.limpar_colecao()

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas sobre os documentos indexados.

        Returns:
            Dicionário com estatísticas.
        """
        documentos = self.listar_documentos()
        total_chunks = vector_store.contar_documentos()

        return {
            "total_documentos": len(documentos),
            "total_chunks": total_chunks,
            "documentos": documentos,
        }


class RAGAgent:
    """Agente RAG principal para perguntas e respostas."""

    def __init__(self):
        """Inicializa o agente RAG."""
        self.document_manager = DocumentManager()
        self.workflow = rag_workflow

    def processar_consulta(
        self,
        consulta: str,
        historico_conversa: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Processa uma consulta do usuário.

        Args:
            consulta: Pergunta do usuário.
            historico_conversa: Histórico de mensagens anteriores.

        Returns:
            Dicionário com a resposta e metadados.
        """
        if historico_conversa is None:
            historico_conversa = []

        # Criar estado inicial
        estado_inicial: AgentState = {
            "consulta": consulta,
            "historico_conversa": historico_conversa,
            "documentos_recuperados": [],
            "contexto": "",
            "resposta": "",
            "fontes": [],
            "precisa_recuperacao": True,
            "erro": None,
        }

        # Executar workflow
        resultado = self.workflow.invoke(estado_inicial)

        # Formatar resposta
        return {
            "resposta": resultado.get("resposta", ""),
            "fontes": resultado.get("fontes", []),
            "num_documentos_usados": len(resultado.get("documentos_recuperados", [])),
            "erro": resultado.get("erro"),
        }

    async def processar_consulta_streaming(
        self,
        consulta: str,
        historico_conversa: Optional[List[Dict[str, str]]] = None,
    ):
        """Processa uma consulta com streaming de resposta.

        Args:
            consulta: Pergunta do usuário.
            historico_conversa: Histórico de mensagens anteriores.

        Yields:
            Chunks da resposta conforme são gerados.
        """
        if historico_conversa is None:
            historico_conversa = []

        # Criar estado inicial
        estado_inicial: AgentState = {
            "consulta": consulta,
            "historico_conversa": historico_conversa,
            "documentos_recuperados": [],
            "contexto": "",
            "resposta": "",
            "fontes": [],
            "precisa_recuperacao": True,
            "erro": None,
        }

        # Executar workflow com streaming
        async for evento in self.workflow.astream(estado_inicial):
            yield evento


# Instância global do agente
rag_agent = RAGAgent()
