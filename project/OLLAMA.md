# 🦙 Guia Ollama - LLM Local

Este guia explica como usar o Ollama como modelo de linguagem local no projeto.

## 🎯 Vantagens do Ollama

- ✅ **100% Gratuito** - Sem custos de API
- ✅ **Privacidade Total** - Dados não saem do seu ambiente
- ✅ **Sem Limites** - Use quanto quiser sem cotas
- ✅ **Offline** - Funciona sem conexão com internet
- ✅ **Rápido** - Baixa latência em hardware adequado

## 📋 Requisitos

### Hardware Mínimo Recomendado

- **CPU**: 4 cores
- **RAM**: 8 GB (16 GB recomendado)
- **Disco**: 10 GB livres
- **GPU**: Opcional (NVIDIA recomendada para melhor performance)

### Modelos Disponíveis

| Modelo | Tamanho | RAM Necessária | Velocidade | Qualidade |
|--------|---------|----------------|------------|-----------|
| llama3 | ~4.7 GB | 8 GB | Rápido | Excelente |
| llama2 | ~3.8 GB | 8 GB | Rápido | Boa |
| mistral | ~4.1 GB | 8 GB | Muito Rápido | Excelente |
| phi | ~1.6 GB | 4 GB | Muito Rápido | Boa |
| codellama | ~3.8 GB | 8 GB | Rápido | Boa (código) |

## 🚀 Configuração Rápida

### 1. Usando Docker Compose (Recomendado)

O projeto já vem configurado com Ollama! Basta iniciar:

```bash
# Copiar configuração de exemplo
cp .env.example .env

# Iniciar todos os serviços (inclui Ollama)
docker-compose up -d

# Aguardar inicialização (1-2 minutos)
docker-compose logs -f ollama
```

### 2. Baixar Modelo Llama3

```bash
# Entrar no container Ollama
docker exec -it ollama-server ollama pull llama3

# Verificar modelos instalados
docker exec -it ollama-server ollama list
```

### 3. Testar Ollama

```bash
# Testar modelo diretamente
docker exec -it ollama-server ollama run llama3 "Olá, como você está?"

# Verificar API
curl http://localhost:11434/api/tags
```

## 🔧 Configuração Manual (Sem Docker)

### Instalar Ollama Localmente

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### macOS
```bash
brew install ollama
```

#### Windows
Baixe o instalador em: https://ollama.com/download/windows

### Iniciar Servidor Ollama

```bash
# Iniciar servidor (porta padrão 11434)
ollama serve

# Em outro terminal, baixar modelo
ollama pull llama3

# Testar
ollama run llama3 "Olá!"
```

### Configurar Aplicação

```bash
# Editar .env
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
LLM_PROVIDER=ollama
LLM_MODEL=llama3
```

## 🎨 Modelos Recomendados por Caso de Uso

### Para Q&A com PDFs (Nosso Caso)
```bash
docker exec -it ollama-server ollama pull llama3
```
- **Modelo**: llama3
- **Motivo**: Excelente compreensão de contexto e português

### Para Código
```bash
docker exec -it ollama-server ollama pull codellama
```
- **Modelo**: codellama
- **Motivo**: Especializado em código

### Para Performance Máxima
```bash
docker exec -it ollama-server ollama pull mistral
```
- **Modelo**: mistral
- **Motivo**: Muito rápido e eficiente

### Para Hardware Limitado
```bash
docker exec -it ollama-server ollama pull phi
```
- **Modelo**: phi
- **Motivo**: Menor e mais leve

## 🔄 Trocar de Modelo

### Via Variável de Ambiente

```bash
# Parar aplicação
docker-compose down

# Editar .env
LLM_MODEL=mistral

# Baixar novo modelo (se necessário)
docker exec -it ollama-server ollama pull mistral

# Reiniciar
docker-compose up -d
```

### Modelos Disponíveis

Ver todos os modelos disponíveis:
```bash
docker exec -it ollama-server ollama list
```

Buscar mais modelos:
- https://ollama.com/library

## 🚀 Otimização de Performance

### Com GPU NVIDIA

1. **Instalar NVIDIA Container Toolkit**:
```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

2. **Descomentar linhas GPU no docker-compose.yml**:
```yaml
ollama:
  image: ollama/ollama:latest
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

3. **Reiniciar**:
```bash
docker-compose down
docker-compose up -d
```

### Verificar Uso de GPU

```bash
# Dentro do container
docker exec -it ollama-server nvidia-smi

# Ver logs do Ollama
docker-compose logs ollama | grep -i gpu
```

## 🐛 Troubleshooting

### Erro: "Failed to pull model"

```bash
# Verificar conectividade
docker exec -it ollama-server curl -I https://ollama.com

# Verificar espaço em disco
docker exec -it ollama-server df -h
```

### Erro: "Connection refused"

```bash
# Verificar se Ollama está rodando
docker-compose ps ollama

# Ver logs
docker-compose logs ollama

# Reiniciar serviço
docker-compose restart ollama
```

### Erro: "Out of Memory"

```bash
# Usar modelo menor
docker exec -it ollama-server ollama pull phi

# Ou aumentar memória do Docker
# Docker Desktop -> Settings -> Resources -> Memory
```

### Respostas Lentas

```bash
# 1. Verificar recursos
docker stats ollama-server

# 2. Usar modelo menor
docker exec -it ollama-server ollama pull mistral

# 3. Atualizar .env
LLM_MODEL=mistral
```

## 📊 Comparação de Velocidade

Tempos médios de resposta (CPU: 8 cores, 16GB RAM):

| Modelo | Tokens/seg | Tempo para 100 palavras |
|--------|------------|-------------------------|
| phi | ~40 | ~5s |
| mistral | ~25 | ~8s |
| llama3 | ~20 | ~10s |
| llama2 | ~18 | ~12s |

Com GPU (NVIDIA RTX 3060):

| Modelo | Tokens/seg | Tempo para 100 palavras |
|--------|------------|-------------------------|
| phi | ~120 | ~2s |
| mistral | ~80 | ~3s |
| llama3 | ~60 | ~4s |
| llama2 | ~55 | ~5s |

## 🔐 Privacidade e Segurança

### Dados Locais

✅ Todo processamento ocorre localmente
✅ PDFs nunca saem do seu ambiente
✅ Sem telemetria ou coleta de dados
✅ Ideal para dados sensíveis ou confidenciais

### Recomendações

- Use Ollama para documentos confidenciais
- Mantenha o Ollama atualizado
- Monitore uso de recursos
- Faça backup dos modelos baixados

## 📚 Recursos Adicionais

- **Site Oficial**: https://ollama.com
- **Documentação**: https://github.com/ollama/ollama
- **Modelos**: https://ollama.com/library
- **Discord**: https://discord.gg/ollama

## 🆘 Suporte

Problemas com Ollama?
1. Verifique os logs: `docker-compose logs ollama`
2. Consulte a documentação oficial
3. Abra uma issue no GitHub do projeto

---

**Desenvolvido para uso local, privado e gratuito! 🦙**
