"""Interface Chainlit para o Simple RAG."""

import chainlit as cl
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from simple_rag.agent.agent import create_agent
from simple_rag.config.config import settings
from simple_rag.utils.logger import setup_logger

logger = setup_logger(__name__)


@cl.on_chat_start
async def start():
    """Inicializa o agente quando o chat inicia."""
    try:
        logger.info("Inicializando agente para nova sessão...")

        # Cria o agente
        agent = create_agent()

        # Get vectorstore instance for PDF uploads
        from simple_rag.tools.retriever import vectorstore

        # Armazena o agente E o vectorstore na sessão do usuário
        cl.user_session.set("agent", agent)
        cl.user_session.set("vectorstore", vectorstore)
        cl.user_session.set("message_history", [])

        # Mensagem de boas-vindas
        welcome_message = f""" # Bem-vindo ao seu Q&A Agent ! 🤓

**Configuração atual:**
- 🤖 Modelo: `{settings.ollama_model}`
- 🗄️ VectorStore: ChromaDB
- 📍 Ollama URL: `{settings.ollama_base_url}`

Faça upload do seu PDF ou Digite sua pergunta para começar!
"""

        await cl.Message(content=welcome_message).send()
        logger.info("✓ Sessão iniciada com sucesso")

    except Exception as e:
        error_msg = f"""❌ **Erro ao inicializar o agente**

Detalhes: {e!s}

**Possíveis soluções:**
1. Verifique se o Ollama está rodando: `ollama serve`
2. Verifique se o modelo está disponível: `ollama pull {settings.ollama_model}`
3. Verifique a URL do Ollama na configuração
"""
        logger.error(f"Erro ao inicializar agente: {e}", exc_info=True)
        await cl.Message(content=error_msg).send()


@cl.on_message
async def main(message: cl.Message):
    """Processa mensagens do usuário."""
    try:
        # Check if files were uploaded with the message
        if message.elements:
            # Filter PDF files
            pdf_files = [
                file for file in message.elements if file.mime == "application/pdf"
            ]

            if pdf_files:
                # Handle PDF uploads
                from simple_rag.utils.pdf_processor import process_pdf_files

                processing_msg = cl.Message(
                    content=f"📄 Processing {len(pdf_files)} PDF file(s)..."
                )
                await processing_msg.send()

                # Get vectorstore from session
                vectorstore = cl.user_session.get("vectorstore")

                if not vectorstore:
                    processing_msg.content = (
                        "❌ Vectorstore not initialized. Please reload."
                    )
                    await processing_msg.update()
                    return

                # Define progress callback to update the UI
                async def update_progress(message: str):
                    processing_msg.content = message
                    await processing_msg.update()

                # Process PDFs with progress updates
                total_chunks, errors = await process_pdf_files(
                    pdf_files, vectorstore, progress_callback=update_progress
                )

                # Provide feedback
                if errors:
                    content = f"✓ Processed {len(pdf_files) - len(errors)} PDF(s) successfully. {total_chunks} chunks added.\n\n"
                    content += f"⚠️ {len(errors)} file(s) failed:\n" + "\n".join(
                        f"• {err}" for err in errors
                    )
                else:
                    content = f"✓ Successfully processed {len(pdf_files)} PDF file(s). {total_chunks} chunks added to knowledge base."

                processing_msg.content = content
                await processing_msg.update()

                logger.info(
                    f"PDF upload completed: {total_chunks} chunks added, {len(errors)} errors"
                )
                return

        # Recupera o agente da sessão
        agent = cl.user_session.get("agent")
        message_history = cl.user_session.get("message_history", [])

        if not agent:
            await cl.Message(
                content="❌ Agente não inicializado. Recarregue a página."
            ).send()
            return

        # Cria mensagem para o agente
        user_message = HumanMessage(content=message.content)

        # Adiciona ao histórico
        message_history.append(user_message)

        # Mensagem de processamento
        processing_msg = cl.Message(content="")
        await processing_msg.send()

        # Processa com o agente
        logger.debug(f"Processando mensagem: {message.content}")

        # Invoca o agente
        result = agent.invoke({"messages": message_history})

        # Processa as respostas
        response_content = ""
        tool_calls_info = []

        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                # Se há tool calls, mostra informação
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get("name", "unknown")
                        tool_args = tool_call.get("args", {})
                        tool_calls_info.append(f"🔧 **{tool_name}**")
                        logger.debug(f"Tool chamada: {tool_name} com args: {tool_args}")

                # Resposta final
                if msg.content:
                    response_content = msg.content
                    message_history.append(msg)

            elif isinstance(msg, ToolMessage):
                # Log de tool messages
                logger.debug(f"Tool result: {msg.content[:100]}...")

        # Atualiza a mensagem com a resposta
        if tool_calls_info:
            tools_section = "\n".join(tool_calls_info)
            final_content = f"{tools_section}\n\n{response_content}"
        else:
            final_content = response_content

        processing_msg.content = final_content
        await processing_msg.update()

        # Atualiza o histórico na sessão
        cl.user_session.set("message_history", message_history)

        # Log de estatísticas
        llm_calls = result.get("llm_calls", 0)
        logger.info(f"✓ Resposta gerada (LLM calls: {llm_calls})")

    except Exception as e:
        error_msg = f"❌ **Erro ao processar mensagem**\n\nDetalhes: {e!s}"
        logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
        await cl.Message(content=error_msg).send()


@cl.on_chat_end
async def end():
    """Cleanup quando o chat termina."""
    logger.info("Sessão encerrada")


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
