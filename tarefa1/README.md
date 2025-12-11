# Tarefa 1: Modelo de Linguagem N-Grama

## Índice
1. [Visão Geral](#visão-geral)
2. [Objetivo](#objetivo)
3. [Arquitetura do Modelo](#arquitetura-do-modelo)
4. [Fluxo de Trabalho](#fluxo-de-trabalho)
5. [Componentes Principais](#componentes-principais)
6. [Detalhamento do Código](#detalhamento-do-código)
7. [Resultados](#resultados)
8. [Requisitos](#requisitos)
9. [Como Executar](#como-executar)

---

## Visão Geral

Este notebook implementa um **Modelo de Linguagem N-Grama** utilizando o algoritmo de **Kneser-Ney Interpolation** para processar e gerar texto em português baseado em proposições legislativas.

Um modelo de linguagem N-Grama estima a probabilidade de uma palavra aparecer dado o contexto das N-1 palavras anteriores. Este tipo de modelo é fundamental em tarefas de:
- Geração de texto
- Correção ortográfica
- Reconhecimento de fala
- Tradução automática

---

## Objetivo

O objetivo principal deste notebook é:

1. **Processar** um dataset de proposições legislativas em português
2. **Tokenizar** o texto usando técnicas de NLP (Natural Language Processing)
3. **Treinar** um modelo de linguagem trigrama (N=3) com suavização Kneser-Ney
4. **Avaliar** a probabilidade de palavras em contextos específicos
5. **Gerar** texto novo baseado em um seed inicial

---

## Arquitetura do Modelo

### Modelo: Kneser-Ney Interpolated Trigram

**Kneser-Ney Interpolation** é uma técnica avançada de suavização que resolve problemas fundamentais em modelos N-Grama:

#### Por que Kneser-Ney?

1. **Problema do Zero**: Sem suavização, se um trigrama nunca apareceu no treino, sua probabilidade seria 0, tornando impossível gerar ou avaliar frases válidas não vistas.

2. **Interpolação**: Combina probabilidades de diferentes ordens de N-Gramas:
   - Trigramas (3 palavras): P(w₃|w₁,w₂)
   - Bigramas (2 palavras): P(w₂|w₁)
   - Unigramas (1 palavra): P(w₁)

3. **Desconto Absoluto**: Redistribui massa de probabilidade de N-Gramas frequentes para N-Gramas raros.

#### Fórmula Simplificada

```
P_KN(w_i | w_{i-2}, w_{i-1}) =
    max(c(w_{i-2}, w_{i-1}, w_i) - δ, 0) / c(w_{i-2}, w_{i-1})
    + λ(w_{i-2}, w_{i-1}) × P_KN(w_i | w_{i-1})
```

Onde:
- `c(...)` = contagem de ocorrências
- `δ` = desconto (geralmente entre 0 e 1)
- `λ` = peso de interpolação

---

## Fluxo de Trabalho

```
┌─────────────────────┐
│  CSV de Proposições │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Carregamento + Join │  ← Concatena textos com separador 'DOCSEP'
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Tokenização spaCy  │  ← Divisão em sentenças e tokens
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Preparação N-Grama  │  ← Adiciona padding <s> e </s>
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Treino Kneser-Ney  │  ← Aprende probabilidades
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Geração de Texto    │  ← Sampling baseado em probabilidades
└─────────────────────┘
```

---

## Componentes Principais

### 1. Bibliotecas Utilizadas

| Biblioteca | Função |
|------------|--------|
| **pandas** | Manipulação de dados tabulares (CSV) |
| **spacy** | Processamento de linguagem natural (tokenização, sentenças) |
| **nltk** | Ferramentas para modelos de linguagem N-Grama |
| **KneserNeyInterpolated** | Implementação do algoritmo de suavização |
| **TreebankWordDetokenizer** | Reconstrução de texto a partir de tokens |

### 2. Dataset

- **Arquivo**: `data/proposicoes.csv`
- **Conteúdo**: Proposições legislativas em português
- **Campo usado**: `texto` (texto completo da proposição)
- **Separador**: `'DOCSEP'` usado para marcar fronteiras entre documentos

### 3. Parâmetros do Modelo

- **N = 3**: Trigrama (considera contexto de 2 palavras anteriores)
- **Tamanho do vocabulário**: 10.531 palavras únicas
- **Tokens especiais**:
  - `<s>`: Início de sentença (start)
  - `</s>`: Fim de sentença (end)
  - `DOCSEP`: Separador de documentos

---

## Detalhamento do Código

### Bloco 1: Importações
```python
import pandas as pd
import nltk
import spacy
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.lm.models import KneserNeyInterpolated
from nltk.tokenize import TreebankWordDetokenizer
```

**Objetivo**: Importar todas as bibliotecas necessárias para:
- Manipulação de dados (pandas)
- Processamento de linguagem natural (spacy, nltk)
- Construção do modelo N-Grama (KneserNeyInterpolated)
- Detokenização (TreebankWordDetokenizer)

---

### Bloco 2: Download do Modelo spaCy
```python
!python -m spacy download pt_core_news_lg
```

**Objetivo**: Baixar o modelo de linguagem portuguesa do spaCy (versão large).

**Por quê?**
- `pt_core_news_lg` é treinado em textos de notícias portuguesas
- Contém 568.2 MB de dados linguísticos (vocabulário, vetores de palavras, regras gramaticais)
- Permite tokenização precisa e divisão em sentenças para português

---

### Bloco 3: Carregamento do Modelo spaCy
```python
nlp = spacy.load("pt_core_news_lg")
```

**Objetivo**: Carregar o pipeline de processamento de texto em português.

**O que acontece internamente?**
- Inicializa tokenizador, tagger, parser e NER (Named Entity Recognition)
- Carrega vetores de palavras para análise semântica
- Configura regras específicas para português brasileiro/europeu

---

### Bloco 4: Carregamento do Dataset
```python
proposicoes = pd.read_csv("data/proposicoes.csv")
proposicoes_txt = ' DOCSEP '.join(list(proposicoes["texto"]))
```

**Objetivo**: Carregar e preparar o corpus de texto.

**Processo**:
1. Lê o CSV contendo proposições legislativas
2. Extrai a coluna `"texto"` de cada proposição
3. Junta todos os textos em uma única string, separados por `' DOCSEP '`

**Por que DOCSEP?**
- Marca fronteiras entre documentos diferentes
- Evita que o modelo aprenda transições impossíveis entre proposições não relacionadas
- Permite adicionar quebras de parágrafo na geração de texto

---

### Bloco 5: Tokenização
```python
doc = nlp(proposicoes_txt)
proposicoes_tok = [[token.text for token in sent] for sent in doc.sents]
```

**Objetivo**: Transformar o texto bruto em uma estrutura de dados tokenizada.

**Processo**:
1. `nlp(proposicoes_txt)`: Processa todo o texto com spaCy
2. `doc.sents`: Divide em sentenças usando regras linguísticas
3. Para cada sentença, extrai o texto de cada token

**Resultado**: Lista de listas
```python
[
  ['Altera', 'a', 'Lei', 'nº', '10861', '...'],
  ['Estabelece', 'diretrizes', 'para', '...'],
  ...
]
```

**Por que tokenizar?**
- Padroniza unidades básicas de texto
- Separa pontuação, números e palavras corretamente
- Permite análise estatística precisa

---

### Bloco 6: Preparação de N-Gramas
```python
N = 3
props_trein, props_vocab = padded_everygram_pipeline(N, proposicoes_tok)
```

**Objetivo**: Criar estruturas de dados adequadas para treino do modelo.

**Parâmetros**:
- `N = 3`: Trigrama (considera 2 palavras de contexto)

**O que `padded_everygram_pipeline` faz?**

1. **Padding**: Adiciona marcadores `<s>` (início) e `</s>` (fim) em cada sentença
   ```python
   ['Altera', 'a', 'Lei'] → ['<s>', '<s>', 'Altera', 'a', 'Lei', '</s>']
   ```

2. **Everygram**: Gera todos os N-Gramas de ordem 1 até N
   - Unigramas: `['<s>']`, `['Altera']`, `['a']`, `['Lei']`
   - Bigramas: `['<s>', 'Altera']`, `['Altera', 'a']`, `['a', 'Lei']`
   - Trigramas: `['<s>', '<s>', 'Altera']`, `['<s>', 'Altera', 'a']`, etc.

**Retorno**:
- `props_trein`: Gerador de N-Gramas para treino
- `props_vocab`: Vocabulário (conjunto de palavras únicas)

**Por que padding?**
- Permite modelar início e fim de sentenças
- Essencial para geração coerente de texto

---

### Bloco 7: Criação do Modelo
```python
lm = KneserNeyInterpolated(N)
```

**Objetivo**: Instanciar o modelo de linguagem.

**Kneser-Ney Interpolated**:
- Algoritmo estado-da-arte para suavização em modelos N-Grama
- Superior a métodos como Laplace ou Good-Turing
- Usa interpolação recursiva entre diferentes ordens de N-Gramas

---

### Bloco 8: Treinamento
```python
lm.fit(props_trein, props_vocab)
len(lm.vocab)  # Retorna: 10531
```

**Objetivo**: Treinar o modelo nos dados tokenizados.

**O que acontece internamente?**

1. **Contagem de N-Gramas**: Para cada trigrama, bigrama e unigrama:
   ```
   Contagem("Altera a Lei") = quantas vezes aparece
   Contagem("a Lei") = quantas vezes aparece
   Contagem("Lei") = quantas vezes aparece
   ```

2. **Cálculo de Probabilidades**: Aplica fórmula Kneser-Ney:
   - Desconto absoluto de contagens
   - Interpolação com N-Gramas de ordem inferior
   - Normalização

3. **Construção do Vocabulário**: 10.531 palavras únicas

**Resultado**: Modelo treinado pronto para scoring e geração

---

### Bloco 9-10: Avaliação de Probabilidades
```python
lm.score('Constituição', ['Altera', 'a'])  # 0.023
lm.score('Lei', ['Altera', 'a'])           # 0.903
```

**Objetivo**: Avaliar quão provável é uma palavra dado um contexto.

**Interpretação**:
- `P("Constituição" | "Altera", "a")` = 2.3%
- `P("Lei" | "Altera", "a")` = 90.3%

**Por que essa diferença?**
- "Altera a Lei" é muito mais comum no corpus legislativo
- "Altera a Constituição" aparece menos frequentemente
- O modelo aprendeu padrões reais da linguagem jurídica

**Aplicação prática**:
- Correção ortográfica: escolher palavra mais provável
- Autocompletar: sugerir próximas palavras
- Detecção de anomalias: frases muito improváveis podem ser erros

---

### Bloco 11: Preparação para Geração
```python
detokenize = TreebankWordDetokenizer().detokenize
```

**Objetivo**: Criar função para reconstruir texto a partir de tokens.

**TreebankWordDetokenizer**:
- Reverte o processo de tokenização
- Adiciona espaços adequados entre palavras
- Gerencia pontuação (ex: não adiciona espaço antes de vírgula)

**Exemplo**:
```python
['Altera', 'a', 'Lei', '.'] → "Altera a Lei."
```

---

### Bloco 12: Geração de Texto
```python
texto_seed = 'Altera a'
texto_gerado = []

for token in lm.generate(300, text_seed=texto_seed.split()):
  if token == '<s>':
    continue  # Ignora marcadores de início
  if token == '</s>':
    break  # Para quando encontra fim de sentença
  if token == 'DOCSEP':
    if texto_gerado[-1] not in [".", "!", "?"]:
      texto_gerado.append(". ")
    texto_gerado.append("\n\n")
    continue
  texto_gerado.append(token)

texto_final = detokenize([t for t in texto_gerado if t not in ["", " "]])
texto_final = texto_final.replace(" \n", "\n").replace("\n ", "\n")
texto_final = texto_final.strip()
```

**Objetivo**: Gerar texto novo baseado em um contexto inicial (seed).

**Processo detalhado**:

1. **Seed**: `"Altera a"` (contexto inicial)

2. **Geração iterativa** (`lm.generate(300, ...)`):
   - A cada passo, o modelo escolhe a próxima palavra baseado nas 2 anteriores
   - Usa sampling probabilístico (não determinístico)
   - Máximo de 300 tokens ou até encontrar `</s>`

3. **Tratamento de tokens especiais**:
   - `<s>`: Ignorado (não aparece no texto final)
   - `</s>`: Interrompe a geração (fim de sentença)
   - `DOCSEP`: Substituído por quebra de parágrafo (`\n\n`)

4. **Pós-processamento**:
   - Se `DOCSEP` aparecer sem pontuação antes, adiciona ponto final
   - Remove espaços extras ao redor de quebras de linha
   - Remove tokens vazios

5. **Detokenização**: Reconstrói texto legível

**Exemplo de saída**:
```
Altera a Lei nº 10861, de 19 de setembro de 2011.
```

**Por que sampling?**
- Gera texto variado (não sempre a palavra mais provável)
- Evita repetições previsíveis
- Permite criatividade controlada por probabilidades

---

## Resultados

### Vocabulário
- **10.531 palavras únicas** aprendidas do corpus

### Probabilidades Avaliadas
| Contexto | Palavra | Probabilidade |
|----------|---------|---------------|
| "Altera a" | "Constituição" | 2.33% |
| "Altera a" | "Lei" | 90.31% |

**Interpretação**: O modelo aprendeu que "Lei" é muito mais provável após "Altera a" no contexto legislativo.

### Texto Gerado
```
Altera a Lei nº 10861, de 19 de setembro de 2011.
```

**Análise**:
- Estrutura gramaticalmente correta
- Segue padrão típico de proposições legislativas
- Número de lei e data são reais do corpus de treino
- Demonstra capacidade de gerar texto coerente

---

## Requisitos

### Dependências Python

```
pandas>=1.5.0
nltk>=3.8
spacy>=3.8.0
```

### Modelos

```bash
python -m spacy download pt_core_news_lg
```

### Dataset

- Arquivo: `tarefa1/data/proposicoes.csv`
- Formato: CSV com coluna `texto` contendo proposições legislativas

---

## Como Executar

### 1. Instalar Dependências

```bash
pip install pandas nltk spacy
python -m spacy download pt_core_news_lg
```

### 2. Preparar Dataset

Certifique-se de que o arquivo `data/proposicoes.csv` existe e contém:
- Coluna `texto` com proposições legislativas em português

### 3. Executar Notebook

```bash
jupyter notebook tarefa1/modelo_linguagem_ngrama.ipynb
```

Ou use Google Colab, VS Code, ou qualquer ambiente Jupyter.

### 4. Executar Células Sequencialmente

Execute todas as células na ordem para:
1. Carregar dados
2. Treinar modelo
3. Avaliar probabilidades
4. Gerar texto

---

## Limitações e Melhorias Futuras

### Limitações

1. **Contexto Limitado**: Trigramas consideram apenas 2 palavras anteriores
2. **Memória**: Não captura dependências de longo alcance
3. **Criatividade**: Pode gerar texto repetitivo ou previsível
4. **Tamanho do Corpus**: Limitado ao dataset de proposições

### Melhorias Possíveis

1. **Aumentar N**: Usar 4-gramas ou 5-gramas (requer mais dados)
2. **Modelos Neurais**: LSTM, Transformers (GPT, BERT)
3. **Beam Search**: Melhorar qualidade da geração
4. **Fine-tuning**: Ajustar para domínios específicos
5. **Avaliação**: Implementar perplexidade para medir qualidade do modelo

---

## Conceitos-Chave

### N-Grama
Sequência de N palavras consecutivas. Exemplos:
- **Unigrama** (N=1): "Lei"
- **Bigrama** (N=2): "Altera a"
- **Trigrama** (N=3): "Altera a Lei"

### Suavização
Técnica para lidar com N-Gramas não vistos no treino, evitando probabilidades zero.

### Perplexidade
Métrica para avaliar modelos de linguagem. Quanto menor, melhor o modelo:
```
Perplexidade = 2^(-log₂ P(texto))
```

### Tokenização
Processo de dividir texto em unidades básicas (tokens):
```
"Altera a Lei." → ["Altera", "a", "Lei", "."]
```

---

## Referências

1. **Kneser-Ney Smoothing**:
   - Kneser, R., & Ney, H. (1995). Improved backing-off for M-gram language modeling.

2. **NLTK Documentation**:
   - https://www.nltk.org/api/nltk.lm.html

3. **spaCy Portuguese Model**:
   - https://spacy.io/models/pt

4. **Language Models**:
   - Jurafsky, D., & Martin, J. H. (2023). Speech and Language Processing (3rd ed.)

---

## Autor

Este notebook faz parte da **Tarefa 1** do curso de Redes Neurais e Transformers.

**Data**: 2025
**Modelo**: Trigrama com Kneser-Ney Interpolation
**Linguagem**: Português (Brasil)