# ============================================================
# agent_core.py — Núcleo del agente TrendScope
# Aquí vive el LLM, las herramientas y la memoria por sesión.
# Patrón: Sesiones 2-3 del seminario de Agentes de IA.
# ============================================================

import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from tools.market_tools import TOOLS

load_dotenv()


# ─── SYSTEM PROMPT ──────────────────────────────────────────
# ✏️ MODIFICA AQUÍ: ajusta el rol y las instrucciones del agente

SYSTEM_PROMPT = """Eres TrendScope, un analista especializado en tendencias del mercado de electrónica de consumo.
Tu función es ayudar a emprendedores, compradores y profesionales de marketing a entender:

* Qué categorías de productos están creciendo
* Qué marcas dominan cada segmento
* Dónde hay oportunidades de negocio o compra inteligente
* Cómo se comparan diferentes opciones en el mercado

Cuando respondas:
* Usa datos concretos (porcentajes, rangos de precio, nombres de marcas)
* Estructura tu respuesta: primero el resumen, luego el detalle
* Si detectas una oportunidad de negocio, menciónala claramente
* Siempre menciona el período de referencia de tus datos (2024-2025)
* Responde en español

No eres un vendedor. Eres un analista objetivo que presenta datos y perspectivas."""


# ─── ALMACÉN DE HISTORIAL EN MEMORIA ────────────────────────
# Cada session_id tiene su propio historial de mensajes.
# En producción puedes reemplazar esto por Redis o una BD.

_store: dict[str, BaseChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Devuelve (o crea) el historial de mensajes para una sesión."""
    if session_id not in _store:
        _store[session_id] = ChatMessageHistory()
    return _store[session_id]


def clear_session(session_id: str) -> bool:
    """Elimina el historial de una sesión. Devuelve True si existía."""
    if session_id in _store:
        del _store[session_id]
        return True
    return False


# ─── CONSTRUCCIÓN DEL LLM ───────────────────────────────────

def _build_llm():
    """
    Construye el LLM según LLM_PROVIDER del .env.
    Soporta 'groq' (en la nube) y 'ollama' (local).
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    temperature = float(os.getenv("TEMPERATURE", "0.5"))
    max_tokens = int(os.getenv("MAX_TOKENS", "1500"))

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=temperature,
        )

    raise ValueError(f"LLM_PROVIDER '{provider}' no soportado. Usa 'groq' u 'ollama'.")


# ─── AGENTE CON HERRAMIENTAS Y MEMORIA ──────────────────────

def build_agent():
    """
    Construye el agente completo usando langgraph.prebuilt.create_react_agent,
    que es compatible con todas las versiones modernas de LangChain/LangGraph
    y soporta herramientas @tool de forma nativa.
    """
    from langgraph.prebuilt import create_react_agent
    from langchain_core.messages import SystemMessage

    llm = _build_llm()

    # create_react_agent maneja el ciclo razonar→herramienta→respuesta internamente
    graph = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )

    return graph


def get_model_name() -> str:
    """Devuelve el nombre del modelo activo (para los schemas de respuesta)."""
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "groq":
        return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    return os.getenv("OLLAMA_MODEL", "llama3.2")
