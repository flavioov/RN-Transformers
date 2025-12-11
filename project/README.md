# 📚 Agente Q&A com PDF usando RAG

Sistema de perguntas e respostas baseado em documentos PDF usando RAG (Retrieval-Augmented Generation), Chainlit, LangGraph e ChromaDB.

## 🎯 Visão Geral

Este projeto demonstra como construir um agente inteligente de Q&A que:

- **Processa documentos PDF** e extrai texto com preservação de metadados
- **Indexa conteúdo** em um banco de dados vetorial (ChromaDB)
- **Responde perguntas** baseado no conteúdo dos documentos
- **Cita fontes** com número de página e relevância
- **Interface interativa** via Chainlit com upload de arquivos
- **Arquitetura modular** usando LangGraph para workflow do agente
- **Totalmente dockerizado** com ChromaDB em container separado

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                      Docker Compose                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  ChromaDB    │  │   Ollama     │  │   RAG App       │   │
│  │  (Vector DB) │  │   (LLM)      │  │   (Chainlit)    │   │
│  │              │  │              │  │                 │   │
│  │  Port: 8001  │◄─┤  Port: 11434 │◄─┤  - PDF Parser  │   │
│  │  (external)  │  │  (external)  │  │  - LangGraph    │   │
│  │              │  │              │  │  - Embeddings   │   │
│  │  Volume:     │  │  Volume:     │  │  - Agent        │   │
│  │  chromadb    │  │  ollama      │  │                 │   │
│  └──────────────┘  └──────────────┘  │  Port: 8000     │   │
│                                       └─────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Componentes Principais

1. **Ollama** - LLM local gratuito (llama3, mistral, etc.) - **RECOMENDADO**
2. **ChromaDB** - Banco de dados vetorial para armazenamento e busca semântica
3. **LangGraph** - Orquestração do workflow do agente (análise → recuperação → geração)
4. **Chainlit** - Interface web interativa para chat e upload de PDFs
5. **LangChain** - Abstrações para LLMs e embeddings
6. **PyMuPDF** - Extração de texto de PDFs

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose instalados
- **8 GB de RAM** (para rodar Ollama com llama3)
- **Opcional**: Chave de API da OpenAI ou Anthropic (se não quiser usar Ollama)

### Instalação e Execução

1. **Clone o repositório**:
```bash
git clone <seu-repositorio>
cd project
```

2. **Configure as variáveis de ambiente**:
```bash
cp .env.example .env
# O arquivo já vem configurado para usar Ollama (gratuito)
# Não precisa de chaves de API!
```

3. **Inicie a aplicação**:
```bash
docker-compose up -d
```

4. **Baixe o modelo Ollama** (primeira vez apenas):
```bash
# Aguarde o Ollama iniciar (1-2 minutos)
docker-compose logs -f ollama

# Baixar llama3.1:8b (~4.7 GB) - modelo padrão
docker exec -it ollama-server ollama pull llama3.1:8b

# Verificar download
docker exec -it ollama-server ollama list
```

5. **Acesse a interface**:
- **Aplicação Chainlit**: http://localhost:8000
- **ChromaDB Admin** (opcional): http://localhost:8001
- **Ollama API** (opcional): http://localhost:11434

6. **Visualize os logs**:
```bash
# Todos os serviços
docker-compose logs -f

# Apenas Ollama
docker-compose logs -f ollama

# Apenas aplicação
docker-compose logs -f rag-app
```

## 📖 Como Usar

### 1. Fazer Upload de PDFs

1. Acesse http://localhost:8000
2. Clique no ícone de anexo (📎)
3. Selecione um ou mais arquivos PDF
4. Aguarde o processamento e indexação

### 2. Fazer Perguntas

Digite suas perguntas no chat. Exemplos:

```
"Quais são os principais tópicos discutidos no documento?"
"Explique o conceito de X mencionado no artigo"
"Quais são as conclusões apresentadas?"
```

### 3. Ver Fontes

As respostas incluem automaticamente:
- Nome do documento fonte
- Número da página
- Score de relevância

## 🛠️ Configuração

### 🦙 Usando Ollama (Padrão - Gratuito)

O projeto vem configurado para usar **Ollama** por padrão, um LLM local e gratuito!

**Modelos suportados**:
- `llama3.1:8b` - **Padrão** - Recomendado (4.7 GB)
- `llama3` - Versão anterior (4.7 GB)
- `mistral` - Mais rápido (4.1 GB)
- `phi` - Mais leve (1.6 GB)
- `codellama` - Para código (3.8 GB)

**Como trocar de modelo**:
```bash
# Baixar novo modelo
docker exec -it ollama-server ollama pull mistral

# Atualizar .env
LLM_MODEL=mistral

# Reiniciar aplicação
docker-compose restart rag-app
```

📖 **Guia completo**: Veja [OLLAMA.md](OLLAMA.md) para detalhes, otimizações e troubleshooting.

### 🔑 Usando APIs Externas (Opcional)

Se preferir usar OpenAI ou Anthropic:

```env
# Configuração LLM
LLM_PROVIDER=openai  # ou anthropic
LLM_MODEL=gpt-4-turbo-preview

# Adicionar chave de API
OPENAI_API_KEY=sua_chave_aqui
```

### Variáveis de Ambiente (.env)

```env
# Ollama (LLM Local) - PADRÃO
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b

# Opcional: APIs externas
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Configuração YAML (config.yaml)

```yaml
chunking:
  tamanho_chunk: 1000
  sobreposicao_chunk: 200
  estrategia: "fixed"

recuperacao:
  top_k: 5
  limiar_similaridade: 0.7
  usar_reranking: false

llm:
  temperatura: 0.7
  max_tokens: 2000
  streaming: true

upload:
  max_tamanho_mb: 50
  formatos_permitidos:
    - "pdf"
```

## 🐳 Comandos Docker

### Desenvolvimento

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Ver logs apenas da aplicação
docker-compose logs -f rag-app

# Ver logs apenas do ChromaDB
docker-compose logs -f chromadb

# Parar serviços
docker-compose down

# Reconstruir a aplicação
docker-compose build rag-app

# Reiniciar apenas a aplicação
docker-compose restart rag-app
```

### Limpeza

```bash
# Parar e remover containers
docker-compose down

# Parar e remover containers + volumes (CUIDADO: apaga dados)
docker-compose down -v

# Remover imagens não utilizadas
docker image prune -a
```

## 📁 Estrutura do Projeto

```
project/
├── src/llm_rag/
│   ├── config.py              # Gerenciamento de configuração
│   ├── embeddings.py          # Modelos de embedding
│   ├── pdf_processor.py       # Processamento de PDF
│   ├── vector_store.py        # Interface ChromaDB
│   ├── agent.py               # Agente principal
│   ├── graph/                 # LangGraph workflow
│   │   ├── state.py          # Estado do grafo
│   │   ├── nodes.py          # Nós do grafo
│   │   └── workflow.py       # Definição do workflow
│   └── ui/
│       └── app.py            # Interface Chainlit
├── tests/                     # Testes
├── data/
│   ├── uploads/              # PDFs enviados
│   └── chroma/               # Dados ChromaDB (em volume)
├── Dockerfile                # Container da aplicação
├── docker-compose.yml        # Orquestração
├── config.yaml              # Configurações
├── .env                     # Variáveis de ambiente
└── pyproject.toml           # Dependências
```

## 🧪 Testes

### Executar Testes Localmente

```bash
# Instalar dependências
poetry install --with dev

# Executar todos os testes
poetry run pytest

# Executar com cobertura
poetry run pytest --cov=llm_rag

# Executar testes específicos
poetry run pytest tests/test_config.py
```

### Executar Testes no Docker

```bash
docker-compose exec rag-app pytest
```

## 🔧 Desenvolvimento Local (Sem Docker)

### 1. Instalar Dependências

```bash
# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependências do projeto
poetry install --with dev

# Ativar ambiente virtual
poetry shell
```

### 2. Configurar Ambiente

```bash
cp .env.example .env
# Editar .env com suas chaves de API
```

### 3. Iniciar ChromaDB Localmente

```bash
# Opção 1: Usar Docker apenas para ChromaDB
docker run -d -p 8001:8000 \
  -v chromadb-data:/chroma/chroma \
  -e IS_PERSISTENT=TRUE \
  chromadb/chroma:latest

# Opção 2: Instalar ChromaDB localmente
pip install chromadb
chroma run --path ./data/chroma --port 8001
```

### 4. Executar Aplicação

```bash
chainlit run src/llm_rag/ui/app.py --host 0.0.0.0 --port 8000
```

## 📊 Workflow do Agente (LangGraph)

```mermaid
graph TD
    A[Início] --> B[Analisar Consulta]
    B -->|Precisa Recuperação| C[Recuperar Documentos]
    B -->|Não Precisa| F[Gerar Resposta]
    C --> D[Formatar Contexto]
    D --> E[Gerar Resposta com Contexto]
    E --> G[Fim]
    F --> G
```

### Nós do Grafo

1. **Analisar Consulta** - Determina se precisa buscar documentos
2. **Recuperar Documentos** - Busca chunks relevantes no ChromaDB
3. **Formatar Contexto** - Organiza documentos recuperados
4. **Gerar Resposta** - Usa LLM para gerar resposta fundamentada

## 🔒 Segurança

- Nunca commite o arquivo `.env` com chaves de API
- Use variáveis de ambiente para informações sensíveis
- Limite o tamanho de upload de PDFs (padrão: 50MB)
- Valide formatos de arquivo antes do processamento

## 🐛 Troubleshooting

### Erro: "Não foi possível conectar ao ChromaDB"

```bash
# Verifique se o ChromaDB está rodando
docker-compose ps

# Verifique os logs do ChromaDB
docker-compose logs chromadb

# Reinicie o ChromaDB
docker-compose restart chromadb
```

### Erro: "OPENAI_API_KEY não configurada"

```bash
# Verifique se o .env existe e está preenchido
cat .env

# Recrie o container com novas variáveis
docker-compose down
docker-compose up -d
```

### Erro: "Out of Memory"

```bash
# Aumente recursos do Docker Desktop
# Ou reduza tamanho dos chunks em config.yaml

chunking:
  tamanho_chunk: 500  # Reduzir de 1000 para 500
```

### PDFs não são processados

```bash
# Verifique permissões do diretório de uploads
ls -la data/uploads/

# Verifique logs da aplicação
docker-compose logs rag-app

# Verifique formato e integridade do PDF
file seu_arquivo.pdf
```

## 📈 Melhorias Futuras

- [ ] Suporte para mais formatos (DOCX, TXT, Markdown)
- [ ] Re-ranking de resultados com modelos especializados
- [ ] Conversational memory com histórico persistente
- [ ] Suporte multi-idioma
- [ ] Autenticação de usuários
- [ ] API REST para integração
- [ ] Métricas e observabilidade (Prometheus + Grafana)
- [ ] Deployment em cloud (AWS, GCP, Azure)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- **Flavio De Oliveira Vieira** - flovieira@rd.com.br

## 🙏 Agradecimentos

- [Chainlit](https://chainlit.io/) - Framework para interfaces de chat
- [LangGraph](https://github.com/langchain-ai/langgraph) - Orquestração de agentes
- [ChromaDB](https://www.trychroma.com/) - Banco de dados vetorial
- [LangChain](https://www.langchain.com/) - Framework LLM
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Manipulação de PDFs

## 📞 Suporte

Para questões e suporte:
- Abra uma issue no GitHub
- Entre em contato: flovieira@rd.com.br

---

**Desenvolvido com ❤️ usando Python, LangChain e Docker**
