# Dockerfile para aplicação RAG com Chainlit
FROM python:3.11-slim

# Metadados
LABEL maintainer="Flavio De Oliveira Vieira <flovieira@rd.com.br>"
LABEL description="Agente Q&A com PDF usando RAG, Chainlit, LangGraph e ChromaDB"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY pyproject.toml poetry.toml ./

# Instalar Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Configurar Poetry para não criar virtualenv
RUN poetry config virtualenvs.create false

# Instalar dependências do projeto
RUN poetry install --no-interaction --no-ansi --no-dev

# Copiar código fonte
COPY src/ ./src/
COPY config.yaml ./

# Criar diretórios necessários
RUN mkdir -p /app/data/uploads /app/data/chroma

# Expor porta do Chainlit
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização
CMD ["chainlit", "run", "src/llm_rag/ui/app.py", "--host", "0.0.0.0", "--port", "8000"]
