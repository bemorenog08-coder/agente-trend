# ============================================================
# chat.py — Endpoint de conversación con memoria por sesión
# El agente recuerda mensajes anteriores dentro de la misma
# session_id. Patrón: Sesión 5 del seminario.
# ============================================================

from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from core.agent_core import build_agent, clear_session, get_session_history, get_model_name

router = APIRouter(prefix="/chat", tags=["Chat"])

# El agente se construye una sola vez al arrancar el servidor.
# ✏️ MODIFICA AQUÍ: si quieres reconstruir el agente por sesión (más lento)
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversa con TrendScope. Cada session_id mantiene su propio
    historial de mensajes (memoria por sesión).
    """
    from langchain_core.messages import HumanMessage

    try:
        agent = get_agent()
        # El historial de la sesión se gestiona manualmente con get_session_history
        historial = get_session_history(request.session_id)
        historial.add_user_message(request.mensaje)

        resultado = agent.invoke({"messages": historial.messages})

        # La última respuesta del AI es el último mensaje de tipo AIMessage
        respuesta_texto = resultado["messages"][-1].content

        # Guardamos la respuesta en el historial de la sesión
        historial.add_ai_message(respuesta_texto)

        return ChatResponse(
            respuesta=respuesta_texto,
            session_id=request.session_id,
            modelo=get_model_name(),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error del agente: {exc}") from exc


@router.delete("/{session_id}")
async def clear_chat(session_id: str):
    """Elimina el historial de una sesión específica."""
    eliminado = clear_session(session_id)
    if eliminado:
        return {"mensaje": f"Historial de sesión '{session_id}' eliminado.", "session_id": session_id}
    return {"mensaje": f"La sesión '{session_id}' no existía o ya estaba vacía.", "session_id": session_id}