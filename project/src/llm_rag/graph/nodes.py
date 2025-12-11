"""Nós do grafo LangGraph para o agente RAG.

Este módulo contém as funções que representam cada nó do grafo de execução.
"""

from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from llm_rag.config import config
from llm_rag.vector_store import vector_store
from llm_rag.graph.state import AgentState


def criar_llm():
    """Cria uma instância do LLM baseado na configuração.

    Returns:
        Instância do LLM configurado.
    """
    provider = config.llm_provider

    if provider == "openai":
        return ChatOpenAI(
            model=config.llm_model,
            temperature=config.llm_temperatura,
            max_tokens=config.llm_max_tokens,
            streaming=config.llm_streaming,
            openai_api_key=config.openai_api_key,
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=config.llm_model,
            temperature=config.llm_temperatura,
            max_tokens=config.llm_max_tokens,
            streaming=config.llm_streaming,
            anthropic_api_key=config.anthropic_api_key,
        )
    elif provider == "ollama":
        return ChatOllama(
            model=config.llm_model,
            temperature=config.llm_temperatura,
            base_url=config.ollama_base_url,
            # Ollama não usa max_tokens da mesma forma, usa num_predict
            num_predict=config.llm_max_tokens,
        )
    else:
        raise ValueError(f"Provedor LLM não suportado: {provider}")


def analisar_consulta(state: AgentState) -> Dict[str, Any]:
    """Analisa a consulta do usuário e determina se precisa recuperar documentos.

    Args:
        state: Estado atual do agente.

    Returns:
        Estado atualizado com flag de necessidade de recuperação.
    """
    consulta = state["consulta"]

    # Por enquanto, sempre assumir que precisa de recuperação
    # Em uma versão mais avançada, poderia usar um LLM para determinar isso
    precisa_recuperacao = True

    # Palavras-chave que indicam saudações ou perguntas gerais
    saudacoes = ["oi", "olá", "bom dia", "boa tarde", "boa noite", "hello", "hi"]
    consulta_lower = consulta.lower().strip()

    if consulta_lower in saudacoes or len(consulta.strip()) < 3:
        precisa_recuperacao = False

    return {
        **state,
        "precisa_recuperacao": precisa_recuperacao,
    }


def recuperar_documentos(state: AgentState) -> Dict[str, Any]:
    """Recupera documentos relevantes do vector store.

    Args:
        state: Estado atual do agente.

    Returns:
        Estado atualizado com documentos recuperados.
    """
    if not state.get("precisa_recuperacao", True):
        return state

    consulta = state["consulta"]

    try:
        # Buscar documentos relevantes
        documentos = vector_store.buscar_documentos(
            consulta=consulta,
            n_resultados=config.retrieval_top_k,
        )

        # Preparar informações das fontes
        fontes = []
        for doc in documentos:
            metadata = doc["metadata"]
            fonte = {
                "documento_nome": metadata.get("documento_nome"),
                "numero_pagina": metadata.get("numero_pagina"),
                "score": doc.get("score"),
            }
            if fonte not in fontes:  # Evitar duplicatas
                fontes.append(fonte)

        return {
            **state,
            "documentos_recuperados": documentos,
            "fontes": fontes,
            "erro": None,
        }

    except Exception as e:
        return {
            **state,
            "documentos_recuperados": [],
            "fontes": [],
            "erro": f"Erro ao recuperar documentos: {str(e)}",
        }


def formatar_contexto(state: AgentState) -> Dict[str, Any]:
    """Formata o contexto a partir dos documentos recuperados.

    Args:
        state: Estado atual do agente.

    Returns:
        Estado atualizado com contexto formatado.
    """
    if not state.get("precisa_recuperacao", True):
        return {**state, "contexto": ""}

    documentos = state.get("documentos_recuperados", [])

    if not documentos:
        return {
            **state,
            "contexto": "Nenhum documento relevante foi encontrado.",
        }

    # Formatar contexto
    contexto_parts = []
    for idx, doc in enumerate(documentos, 1):
        metadata = doc["metadata"]
        texto = doc["texto"]
        doc_nome = metadata.get("documento_nome", "Desconhecido")
        pagina = metadata.get("numero_pagina", "?")
        score = doc.get("score", 0)

        contexto_parts.append(
            f"[Documento {idx}: {doc_nome} - Página {pagina} - Relevância: {score:.2f}]\n{texto}\n"
        )

    contexto = "\n---\n".join(contexto_parts)

    return {**state, "contexto": contexto}


def gerar_resposta(state: AgentState) -> Dict[str, Any]:
    """Gera resposta usando o LLM com o contexto recuperado.

    Args:
        state: Estado atual do agente.

    Returns:
        Estado atualizado com a resposta gerada.
    """
    consulta = state["consulta"]
    contexto = state.get("contexto", "")
    historico = state.get("historico_conversa", [])
    precisa_recuperacao = state.get("precisa_recuperacao", True)

    try:
        llm = criar_llm()

        # Preparar prompt baseado se precisa ou não de recuperação
        if precisa_recuperacao and contexto:
            system_prompt = """Você é um assistente útil que responde perguntas baseado em documentos fornecidos.

INSTRUÇÕES IMPORTANTES:
- Responda APENAS com base no contexto fornecido
- Se a informação não estiver no contexto, diga claramente que não encontrou a informação
- Cite o número da página quando possível
- Seja claro, conciso e objetivo
- Responda em português brasileiro

CONTEXTO:
{contexto}

Responda à pergunta do usuário baseado apenas no contexto acima."""

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{consulta}"),
                ]
            )

            mensagens = prompt.format_messages(
                contexto=contexto, consulta=consulta
            )

        else:
            # Resposta sem contexto (saudação ou pergunta geral)
            system_prompt = """Você é um assistente útil especializado em responder perguntas sobre documentos PDF.

Se o usuário cumprimentar você, seja cordial e explique brevemente o que você pode fazer.
Se for uma pergunta que requer documentos, informe que nenhum documento foi encontrado ou carregado ainda.

Responda sempre em português brasileiro."""

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{consulta}"),
                ]
            )

            mensagens = prompt.format_messages(consulta=consulta)

        # Gerar resposta
        resposta_llm = llm.invoke(mensagens)
        resposta = resposta_llm.content

        return {
            **state,
            "resposta": resposta,
            "erro": None,
        }

    except Exception as e:
        return {
            **state,
            "resposta": f"Desculpe, ocorreu um erro ao gerar a resposta: {str(e)}",
            "erro": str(e),
        }


def decidir_proximo_no(state: AgentState) -> str:
    """Decide qual o próximo nó a executar baseado no estado.

    Args:
        state: Estado atual do agente.

    Returns:
        Nome do próximo nó.
    """
    if state.get("erro"):
        return "fim"

    if not state.get("precisa_recuperacao", True):
        return "gerar"

    return "recuperar"
