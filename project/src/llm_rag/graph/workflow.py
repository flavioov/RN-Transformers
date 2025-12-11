"""Workflow principal do agente RAG usando LangGraph.

Este módulo define o grafo completo de execução do agente.
"""

from langgraph.graph import StateGraph, END

from llm_rag.graph.state import AgentState
from llm_rag.graph.nodes import (
    analisar_consulta,
    recuperar_documentos,
    formatar_contexto,
    gerar_resposta,
    decidir_proximo_no,
)


def criar_workflow() -> StateGraph:
    """Cria e configura o workflow do agente RAG.

    Returns:
        Grafo de estado compilado pronto para execução.
    """
    # Criar o grafo
    workflow = StateGraph(AgentState)

    # Adicionar nós
    workflow.add_node("analisar", analisar_consulta)
    workflow.add_node("recuperar", recuperar_documentos)
    workflow.add_node("formatar", formatar_contexto)
    workflow.add_node("gerar", gerar_resposta)

    # Definir ponto de entrada
    workflow.set_entry_point("analisar")

    # Adicionar arestas condicionais
    workflow.add_conditional_edges(
        "analisar",
        decidir_proximo_no,
        {
            "recuperar": "recuperar",
            "gerar": "gerar",
            "fim": END,
        },
    )

    # Adicionar arestas normais
    workflow.add_edge("recuperar", "formatar")
    workflow.add_edge("formatar", "gerar")
    workflow.add_edge("gerar", END)

    # Compilar o grafo
    app = workflow.compile()

    return app


# Instância global do workflow
rag_workflow = criar_workflow()
