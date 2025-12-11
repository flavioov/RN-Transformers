"""Módulo para gerenciamento do ChromaDB como vector store.

Este módulo fornece interface para conectar ao servidor ChromaDB e realizar
operações de indexação e busca de documentos.
"""

import time
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings

from llm_rag.config import config
from llm_rag.embeddings import embedding_manager
from llm_rag.pdf_processor import DocumentChunk


class VectorStore:
    """Gerenciador do ChromaDB como cliente remoto."""

    def __init__(self, max_retries: int = 5, retry_delay: int = 2):
        """Inicializa conexão com servidor ChromaDB.

        Args:
            max_retries: Número máximo de tentativas de conexão.
            retry_delay: Delay entre tentativas em segundos.

        Raises:
            ConnectionError: Se não conseguir conectar após todas as tentativas.
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = self._conectar_chromadb()
        self.collection = None

    def _conectar_chromadb(self):
        """Conecta ao servidor ChromaDB com retry logic.

        Returns:
            Cliente ChromaDB conectado.

        Raises:
            ConnectionError: Se não conseguir conectar.
        """
        chroma_host = config.chroma_host
        chroma_port = config.chroma_port

        for tentativa in range(1, self.max_retries + 1):
            try:
                client = chromadb.HttpClient(
                    host=chroma_host,
                    port=chroma_port,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                    ),
                )

                # Testar conexão
                client.heartbeat()

                if config.debug:
                    print(
                        f"✓ Conectado ao ChromaDB em {chroma_host}:{chroma_port}"
                    )

                return client

            except Exception as e:
                if tentativa < self.max_retries:
                    if config.debug:
                        print(
                            f"✗ Tentativa {tentativa}/{self.max_retries} falhou. "
                            f"Tentando novamente em {self.retry_delay}s..."
                        )
                    time.sleep(self.retry_delay)
                else:
                    raise ConnectionError(
                        f"Não foi possível conectar ao ChromaDB em "
                        f"{chroma_host}:{chroma_port} após {self.max_retries} tentativas. "
                        f"Erro: {str(e)}"
                    )

    def criar_colecao(
        self,
        nome: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Cria ou obtém uma coleção existente.

        Args:
            nome: Nome da coleção. Se None, usa o padrão da configuração.
            metadata: Metadados da coleção.

        Returns:
            Coleção ChromaDB.
        """
        if nome is None:
            nome = config.chroma_colecao

        if metadata is None:
            metadata = {"descricao": "Coleção de documentos PDF para RAG"}

        # Obter ou criar coleção
        self.collection = self.client.get_or_create_collection(
            name=nome,
            metadata=metadata,
            # Usar métrica de distância configurada
            embedding_function=None,  # Vamos gerenciar embeddings manualmente
        )

        if config.debug:
            print(f"✓ Coleção '{nome}' pronta para uso")

        return self.collection

    def adicionar_documentos(self, chunks: List[DocumentChunk]) -> int:
        """Adiciona chunks de documentos ao vector store.

        Args:
            chunks: Lista de chunks a serem indexados.

        Returns:
            Número de chunks adicionados.

        Raises:
            ValueError: Se a coleção não foi criada.
        """
        if self.collection is None:
            raise ValueError("Coleção não foi criada. Execute criar_colecao() primeiro.")

        if not chunks:
            return 0

        # Preparar dados para indexação
        textos = [chunk.texto for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        # Gerar embeddings
        if config.debug:
            print(f"Gerando embeddings para {len(textos)} chunks...")

        embeddings = embedding_manager.embed_documents(textos)

        # Adicionar à coleção
        self.collection.add(
            embeddings=embeddings,
            documents=textos,
            metadatas=metadatas,
            ids=ids,
        )

        if config.debug:
            print(f"✓ {len(chunks)} chunks adicionados ao vector store")

        return len(chunks)

    def buscar_documentos(
        self,
        consulta: str,
        n_resultados: Optional[int] = None,
        filtro_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Busca documentos similares à consulta.

        Args:
            consulta: Texto da consulta.
            n_resultados: Número de resultados a retornar. Se None, usa configuração.
            filtro_metadata: Filtros adicionais por metadados.

        Returns:
            Lista de documentos relevantes com metadados e scores.

        Raises:
            ValueError: Se a coleção não foi criada.
        """
        if self.collection is None:
            raise ValueError("Coleção não foi criada. Execute criar_colecao() primeiro.")

        if n_resultados is None:
            n_resultados = config.retrieval_top_k

        # Gerar embedding da consulta
        query_embedding = embedding_manager.embed_query(consulta)

        # Buscar documentos similares
        resultados = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_resultados,
            where=filtro_metadata,
            include=["documents", "metadatas", "distances"],
        )

        # Formatar resultados
        documentos = []
        if resultados["documents"] and len(resultados["documents"]) > 0:
            for idx in range(len(resultados["documents"][0])):
                # Calcular score de similaridade (inverso da distância)
                distancia = resultados["distances"][0][idx]
                # Para distância cosseno, converter para similaridade
                similaridade = 1 - distancia

                # Aplicar limiar de similaridade
                if similaridade >= config.retrieval_similarity_threshold:
                    doc = {
                        "texto": resultados["documents"][0][idx],
                        "metadata": resultados["metadatas"][0][idx],
                        "score": round(similaridade, 4),
                        "distancia": round(distancia, 4),
                    }
                    documentos.append(doc)

        return documentos

    def deletar_documento(self, documento_id: str) -> int:
        """Deleta todos os chunks de um documento.

        Args:
            documento_id: ID do documento a ser deletado.

        Returns:
            Número de chunks deletados.

        Raises:
            ValueError: Se a coleção não foi criada.
        """
        if self.collection is None:
            raise ValueError("Coleção não foi criada. Execute criar_colecao() primeiro.")

        # Buscar todos os chunks do documento
        resultados = self.collection.get(
            where={"documento_id": documento_id},
            include=["metadatas"],
        )

        if resultados["ids"]:
            # Deletar chunks
            self.collection.delete(ids=resultados["ids"])

            if config.debug:
                print(f"✓ {len(resultados['ids'])} chunks deletados do documento '{documento_id}'")

            return len(resultados["ids"])

        return 0

    def listar_documentos(self) -> List[Dict[str, Any]]:
        """Lista todos os documentos únicos na coleção.

        Returns:
            Lista de documentos com informações básicas.

        Raises:
            ValueError: Se a coleção não foi criada.
        """
        if self.collection is None:
            raise ValueError("Coleção não foi criada. Execute criar_colecao() primeiro.")

        # Obter todos os metadados
        resultados = self.collection.get(include=["metadatas"])

        # Agrupar por documento_id
        documentos_map = {}
        for metadata in resultados["metadatas"]:
            doc_id = metadata.get("documento_id")
            if doc_id and doc_id not in documentos_map:
                documentos_map[doc_id] = {
                    "documento_id": doc_id,
                    "documento_nome": metadata.get("documento_nome"),
                    "total_paginas": metadata.get("total_paginas"),
                    "num_chunks": 0,
                }
            if doc_id:
                documentos_map[doc_id]["num_chunks"] += 1

        return list(documentos_map.values())

    def contar_documentos(self) -> int:
        """Conta o número total de chunks na coleção.

        Returns:
            Número de chunks indexados.

        Raises:
            ValueError: Se a coleção não foi criada.
        """
        if self.collection is None:
            raise ValueError("Coleção não foi criada. Execute criar_colecao() primeiro.")

        return self.collection.count()

    def limpar_colecao(self):
        """Remove todos os documentos da coleção.

        Raises:
            ValueError: Se a coleção não foi criada.
        """
        if self.collection is None:
            raise ValueError("Coleção não foi criada. Execute criar_colecao() primeiro.")

        # Deletar a coleção e recriar
        nome_colecao = self.collection.name
        self.client.delete_collection(name=nome_colecao)
        self.criar_colecao(nome=nome_colecao)

        if config.debug:
            print(f"✓ Coleção '{nome_colecao}' limpa")


# Instância global do vector store
vector_store = VectorStore()
