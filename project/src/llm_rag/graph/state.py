"""Definição do estado do grafo LangGraph.

Este módulo define a estrutura de estado que é passada entre os nós do grafo.
"""

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Estado do agente RAG.

    Attributes:
        consulta: Pergunta do usuário.
        historico_conversa: Histórico de mensagens da conversa.
        documentos_recuperados: Documentos relevantes recuperados do vector store.
        contexto: Contexto formatado para o LLM.
        resposta: Resposta gerada pelo LLM.
        fontes: Informações sobre as fontes usadas na resposta.
        precisa_recuperacao: Flag indicando se precisa fazer recuperação.
        erro: Mensagem de erro, se houver.
    """

    consulta: str
    historico_conversa: List[Dict[str, str]]
    documentos_recuperados: List[Dict[str, Any]]
    contexto: str
    resposta: str
    fontes: List[Dict[str, Any]]
    precisa_recuperacao: bool
    erro: Optional[str]
