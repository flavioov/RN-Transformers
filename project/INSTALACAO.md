# 🚀 Guia de Instalação Rápida

## Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Docker instalado (versão 20.10+)
- ✅ Docker Compose instalado (versão 2.0+)
- ✅ Chave de API da OpenAI ou Anthropic

## Passo a Passo

### 1. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar e adicionar sua chave de API
nano .env  # ou use seu editor preferido
```

No arquivo `.env`, configure:

```env
# Obrigatório: Adicione pelo menos uma chave de API
OPENAI_API_KEY=sk-...
# OU
ANTHROPIC_API_KEY=sk-ant-...

# Opcional: Personalizar configurações
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
```

### 2. Iniciar Aplicação

```bash
# Construir e iniciar todos os serviços
docker-compose up -d

# Aguardar inicialização (30-60 segundos)
docker-compose logs -f
```

### 3. Acessar Interface

Abra seu navegador em: **http://localhost:8000**

## Verificação

### Verificar Status dos Containers

```bash
docker-compose ps
```

Você deve ver:

```
NAME                STATUS              PORTS
chromadb-server     Up 30 seconds       0.0.0.0:8001->8000/tcp
rag-chainlit-app    Up 30 seconds       0.0.0.0:8000->8000/tcp
```

### Verificar Logs

```bash
# Logs da aplicação
docker-compose logs rag-app

# Logs do ChromaDB
docker-compose logs chromadb
```

## Primeiro Uso

1. **Acesse**: http://localhost:8000
2. **Upload**: Clique no ícone 📎 e envie um PDF
3. **Aguarde**: O processamento e indexação do documento
4. **Pergunte**: Digite sua primeira pergunta sobre o documento

## Comandos Úteis

```bash
# Parar aplicação
docker-compose down

# Reiniciar aplicação
docker-compose restart

# Ver logs em tempo real
docker-compose logs -f

# Atualizar código e reiniciar
docker-compose down
docker-compose build
docker-compose up -d
```

## Solução de Problemas Comuns

### Erro: "Port already in use"

```bash
# Verificar processo usando a porta 8000
lsof -i :8000

# OU mudar porta no docker-compose.yml
ports:
  - "8080:8000"  # Usar porta 8080 em vez de 8000
```

### Erro: "Cannot connect to ChromaDB"

```bash
# Aguardar mais tempo (ChromaDB pode demorar para iniciar)
docker-compose logs chromadb

# Verificar health check
docker inspect chromadb-server | grep Health
```

### Erro: "API key not found"

```bash
# Verificar se .env foi criado
cat .env

# Recriar containers com novas variáveis
docker-compose down
docker-compose up -d
```

## Próximos Passos

- 📖 Leia o [README.md](README.md) completo
- 🧪 Execute os testes: `docker-compose exec rag-app pytest`
- ⚙️ Personalize [config.yaml](config.yaml)
- 🔧 Explore desenvolvimento local no README

## Suporte

Problemas? Entre em contato:
- 📧 Email: flovieira@rd.com.br
- 🐛 Issues: GitHub Issues

---

**Boa sorte com seu agente de Q&A! 🎉**
