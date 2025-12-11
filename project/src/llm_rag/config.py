"""Módulo de gerenciamento de configurações da aplicação.

Este módulo carrega e valida configurações de variáveis de ambiente e arquivos YAML.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """Classe para gerenciar configurações da aplicação."""

    def __init__(self, config_path: Optional[str] = None):
        """Inicializa o gerenciador de configurações.

        Args:
            config_path: Caminho para o arquivo de configuração YAML.
                        Se None, usa o padrão config.yaml na raiz do projeto.
        """
        # Carregar variáveis de ambiente
        load_dotenv()

        # Carregar configurações do arquivo YAML
        if config_path is None:
            # Busca config.yaml na raiz do projeto
            current_dir = Path(__file__).parent
            config_path = current_dir.parent.parent / "config.yaml"

        self.config_data = self._carregar_yaml(config_path)

        # Validar configurações obrigatórias
        self._validar_configuracoes()

    def _carregar_yaml(self, caminho: Path) -> Dict[str, Any]:
        """Carrega configurações do arquivo YAML.

        Args:
            caminho: Caminho para o arquivo YAML.

        Returns:
            Dicionário com as configurações carregadas.
        """
        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: {caminho}"
            )

        with open(caminho, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _validar_configuracoes(self):
        """Valida se as configurações obrigatórias estão presentes."""
        # Validar chave de API do LLM
        provider = self.llm_provider
        if provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada")
        elif provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY não configurada")

    # Configurações ChromaDB
    @property
    def chroma_host(self) -> str:
        """Retorna o host do servidor ChromaDB."""
        return os.getenv("CHROMA_HOST", "localhost")

    @property
    def chroma_port(self) -> int:
        """Retorna a porta do servidor ChromaDB."""
        return int(os.getenv("CHROMA_PORT", "8001"))

    @property
    def chroma_colecao(self) -> str:
        """Retorna o nome da coleção ChromaDB."""
        return self.config_data.get("chromadb", {}).get(
            "nome_colecao", "documentos_pdf"
        )

    @property
    def chroma_distancia(self) -> str:
        """Retorna a métrica de distância para ChromaDB."""
        return self.config_data.get("chromadb", {}).get("distancia_metrica", "cosine")

    # Configurações LLM
    @property
    def llm_provider(self) -> str:
        """Retorna o provedor de LLM (openai ou anthropic)."""
        return os.getenv("LLM_PROVIDER", "openai")

    @property
    def llm_model(self) -> str:
        """Retorna o modelo LLM a ser usado."""
        return os.getenv("LLM_MODEL", "llama")

    @property
    def llm_temperatura(self) -> float:
        """Retorna a temperatura do LLM."""
        return float(self.config_data.get("llm", {}).get("temperatura", 0.7))

    @property
    def llm_max_tokens(self) -> int:
        """Retorna o número máximo de tokens para o LLM."""
        return int(self.config_data.get("llm", {}).get("max_tokens", 2000))

    @property
    def llm_streaming(self) -> bool:
        """Retorna se deve usar streaming nas respostas."""
        return bool(self.config_data.get("llm", {}).get("streaming", True))

    @property
    def openai_api_key(self) -> Optional[str]:
        """Retorna a chave de API da OpenAI."""
        return os.getenv("OPENAI_API_KEY")

    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Retorna a chave de API da Anthropic."""
        return os.getenv("ANTHROPIC_API_KEY")

    # Configurações de Embedding
    @property
    def embedding_model(self) -> str:
        """Retorna o modelo de embedding a ser usado."""
        return os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Configurações de Chunking
    @property
    def chunk_size(self) -> int:
        """Retorna o tamanho dos chunks de texto."""
        return int(self.config_data.get("chunking", {}).get("tamanho_chunk", 1000))

    @property
    def chunk_overlap(self) -> int:
        """Retorna a sobreposição entre chunks."""
        return int(self.config_data.get("chunking", {}).get("sobreposicao_chunk", 200))

    @property
    def chunk_strategy(self) -> str:
        """Retorna a estratégia de chunking (fixed ou semantic)."""
        return self.config_data.get("chunking", {}).get("estrategia", "fixed")

    # Configurações de Recuperação
    @property
    def retrieval_top_k(self) -> int:
        """Retorna o número de documentos a recuperar."""
        return int(self.config_data.get("recuperacao", {}).get("top_k", 5))

    @property
    def retrieval_similarity_threshold(self) -> float:
        """Retorna o limiar de similaridade para recuperação."""
        return float(
            self.config_data.get("recuperacao", {}).get("limiar_similaridade", 0.7)
        )

    @property
    def usar_reranking(self) -> bool:
        """Retorna se deve usar re-ranking nos resultados."""
        return bool(
            self.config_data.get("recuperacao", {}).get("usar_reranking", False)
        )

    # Configurações de Upload
    @property
    def upload_max_size_mb(self) -> int:
        """Retorna o tamanho máximo de upload em MB."""
        return int(self.config_data.get("upload", {}).get("max_tamanho_mb", 50))

    @property
    def upload_allowed_formats(self) -> list:
        """Retorna os formatos de arquivo permitidos."""
        return self.config_data.get("upload", {}).get("formatos_permitidos", ["pdf"])

    @property
    def upload_directory(self) -> str:
        """Retorna o diretório de uploads."""
        return self.config_data.get("upload", {}).get(
            "diretorio_uploads", "./data/uploads"
        )

    # Configurações da Aplicação
    @property
    def app_name(self) -> str:
        """Retorna o nome da aplicação."""
        return self.config_data.get("app", {}).get("nome", "Agente Q&A com PDF")

    @property
    def app_version(self) -> str:
        """Retorna a versão da aplicação."""
        return self.config_data.get("app", {}).get("versao", "0.1.0")

    @property
    def app_description(self) -> str:
        """Retorna a descrição da aplicação."""
        return self.config_data.get("app", {}).get(
            "descricao",
            "Sistema de perguntas e respostas baseado em documentos PDF usando RAG",
        )

    @property
    def debug(self) -> bool:
        """Retorna se o modo debug está ativado."""
        return os.getenv("DEBUG", "False").lower() == "true"


# Instância global de configuração
config = Config()
