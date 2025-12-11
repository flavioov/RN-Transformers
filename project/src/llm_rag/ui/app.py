"""Aplicação Chainlit para interface de Q&A com PDF.

Este módulo implementa a interface web interativa usando Chainlit.
"""

import asyncio
from pathlib import Path
from typing import Optional

import chainlit as cl

from llm_rag.agent import rag_agent
from llm_rag.config import config


@cl.on_chat_start
async def on_chat_start():
    """Callback executado quando uma nova sessão de chat é iniciada."""
    # Mensagem de boas-vindas
    mensagem_boas_vindas = f"""# 👋 Bem-vindo ao {config.app_name}!

{config.app_description}

## 📚 Como usar:

1. **Faça upload de um PDF**: Use o botão de anexo (📎) para enviar seus documentos
2. **Faça perguntas**: Após o upload, pergunte qualquer coisa sobre o conteúdo
3. **Veja as fontes**: As respostas incluem referências às páginas dos documentos

## ℹ️ Informações:
- **Versão**: {config.app_version}
- **Modelo LLM**: {config.llm_model}
- **Provedor**: {config.llm_provider}

Comece fazendo o upload de um PDF ou digite uma mensagem!
"""

    await cl.Message(content=mensagem_boas_vindas).send()

    # Inicializar histórico de conversa na sessão
    cl.user_session.set("historico", [])

    # Mostrar estatísticas de documentos indexados
    stats = rag_agent.document_manager.obter_estatisticas()
    if stats["total_documentos"] > 0:
        docs_info = "\n".join(
            [
                f"- **{doc['documento_nome']}** ({doc['total_paginas']} páginas, {doc['num_chunks']} chunks)"
                for doc in stats["documentos"]
            ]
        )
        await cl.Message(
            content=f"""## 📄 Documentos já indexados ({stats['total_documentos']}):

{docs_info}

Total de chunks indexados: {stats['total_chunks']}"""
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Callback executado quando o usuário envia uma mensagem.

    Args:
        message: Mensagem do usuário.
    """
    # Obter histórico da sessão
    historico = cl.user_session.get("historico")

    # Processar arquivos anexados
    if message.elements:
        await processar_arquivos(message.elements)

    # Processar consulta
    consulta = message.content

    if not consulta.strip():
        return

    # Criar mensagem de resposta com streaming
    msg = cl.Message(content="")
    await msg.send()

    try:
        # Processar consulta
        resultado = rag_agent.processar_consulta(
            consulta=consulta,
            historico_conversa=historico,
        )

        # Exibir resposta
        resposta = resultado["resposta"]
        await msg.update(content=resposta)

        # Adicionar fontes se houver
        fontes = resultado.get("fontes", [])
        if fontes:
            fontes_texto = "\n\n---\n\n**📚 Fontes consultadas:**\n\n"
            fontes_vistas = set()

            for fonte in fontes:
                doc_nome = fonte.get("documento_nome", "Desconhecido")
                pagina = fonte.get("numero_pagina", "?")
                score = fonte.get("score", 0)

                fonte_id = f"{doc_nome}_p{pagina}"
                if fonte_id not in fontes_vistas:
                    fontes_texto += f"- 📄 **{doc_nome}** - Página {pagina} (Relevância: {score:.2%})\n"
                    fontes_vistas.add(fonte_id)

            await msg.update(content=resposta + fontes_texto)

        # Atualizar histórico
        historico.append({"role": "user", "content": consulta})
        historico.append({"role": "assistant", "content": resposta})
        cl.user_session.set("historico", historico)

    except Exception as e:
        await msg.update(content=f"❌ Erro ao processar consulta: {str(e)}")


async def processar_arquivos(elements):
    """Processa arquivos PDF anexados pelo usuário.

    Args:
        elements: Lista de elementos anexados.
    """
    for element in elements:
        if isinstance(element, cl.File):
            # Verificar se é PDF
            if not element.name.lower().endswith(".pdf"):
                await cl.Message(
                    content=f"⚠️ Arquivo **{element.name}** não é um PDF e foi ignorado."
                ).send()
                continue

            # Mostrar mensagem de processamento
            msg_processamento = cl.Message(
                content=f"⏳ Processando PDF: **{element.name}**..."
            )
            await msg_processamento.send()

            try:
                # Salvar arquivo temporariamente
                caminho_pdf = Path(element.path)

                # Indexar PDF
                resultado = rag_agent.document_manager.indexar_pdf(caminho_pdf)

                # Mensagem de sucesso
                await msg_processamento.update(
                    content=f"""✅ PDF **{resultado['documento_nome']}** indexado com sucesso!

📊 **Informações:**
- Total de páginas: {resultado['total_paginas']}
- Tamanho: {resultado['tamanho_mb']} MB
- Chunks criados: {resultado['num_chunks']}

Agora você pode fazer perguntas sobre este documento!"""
                )

            except Exception as e:
                await msg_processamento.update(
                    content=f"❌ Erro ao processar PDF **{element.name}**: {str(e)}"
                )


@cl.action_callback("listar_documentos")
async def listar_documentos_callback(action: cl.Action):
    """Callback para listar documentos indexados.

    Args:
        action: Ação do Chainlit.
    """
    stats = rag_agent.document_manager.obter_estatisticas()

    if stats["total_documentos"] == 0:
        await cl.Message(content="📭 Nenhum documento indexado ainda.").send()
        return

    docs_info = "\n".join(
        [
            f"{idx}. **{doc['documento_nome']}**\n"
            f"   - ID: `{doc['documento_id']}`\n"
            f"   - Páginas: {doc['total_paginas']}\n"
            f"   - Chunks: {doc['num_chunks']}\n"
            for idx, doc in enumerate(stats["documentos"], 1)
        ]
    )

    await cl.Message(
        content=f"""## 📄 Documentos Indexados ({stats['total_documentos']}):

{docs_info}

**Total de chunks:** {stats['total_chunks']}"""
    ).send()


@cl.action_callback("limpar_documentos")
async def limpar_documentos_callback(action: cl.Action):
    """Callback para limpar todos os documentos.

    Args:
        action: Ação do Chainlit.
    """
    try:
        rag_agent.document_manager.limpar_todos_documentos()
        await cl.Message(content="🗑️ Todos os documentos foram removidos.").send()
    except Exception as e:
        await cl.Message(content=f"❌ Erro ao limpar documentos: {str(e)}").send()


@cl.on_settings_update
async def on_settings_update(settings):
    """Callback executado quando as configurações são atualizadas.

    Args:
        settings: Novas configurações.
    """
    await cl.Message(
        content=f"✅ Configurações atualizadas: {settings}"
    ).send()


# Configurar settings do Chainlit
@cl.set_chat_profiles
async def chat_profile():
    """Define perfis de chat disponíveis."""
    return [
        cl.ChatProfile(
            name="RAG Q&A",
            markdown_description="Modo padrão de perguntas e respostas com PDFs",
            icon="📚",
        ),
    ]


if __name__ == "__main__":
    # Executar aplicação
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
