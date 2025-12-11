#!/bin/bash
# Script de inicialização para garantir que ChromaDB e Ollama estão prontos

set -e

echo "🚀 Iniciando aplicação RAG..."

# Função para aguardar serviço estar pronto
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    echo "⏳ Aguardando $service_name em $host:$port..."

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://$host:$port" > /dev/null 2>&1; then
            echo "✅ $service_name está pronto!"
            return 0
        fi

        echo "   Tentativa $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ Falha ao conectar com $service_name após $max_attempts tentativas"
    return 1
}

# Aguardar ChromaDB
if ! wait_for_service "${CHROMA_HOST:-chromadb}" "${CHROMA_PORT:-8000}" "ChromaDB"; then
    echo "⚠️  ChromaDB não está respondendo, mas continuando..."
fi

# Aguardar Ollama (se estiver usando)
if [ "${LLM_PROVIDER:-ollama}" = "ollama" ] || [ "${LLM_PROVIDER}" = "llama" ]; then
    if ! wait_for_service "${OLLAMA_HOST:-ollama}" "${OLLAMA_PORT:-11434}" "Ollama"; then
        echo "⚠️  Ollama não está respondendo, mas continuando..."
    fi
fi

echo "🎉 Todos os serviços estão prontos!"
echo "🚀 Iniciando Chainlit..."

# Executar comando passado como argumento ou comando padrão
exec "$@"
