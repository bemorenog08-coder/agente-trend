# ============================================================
# trend_graph.py — Grafo condicional LangGraph
# Implementa el flujo de clasificación → análisis especializado.
# Patrón: Sesión 4 del seminario de Agentes de IA.
#
# Flujo:
#   START → nodo_clasificar → router → nodo_tendencia
#                                    → nodo_comparacion
#                                    → nodo_oportunidad
#                                    → nodo_general
#                             ↓
#                            END
# ============================================================

import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()


# ─── ESTADO DEL GRAFO ───────────────────────────────────────
# TypedDict define los campos que viajan entre nodos.
# add_messages acumula mensajes en lugar de reemplazarlos.

class TrendState(TypedDict):
    mensajes: Annotated[list, add_messages]   # historial de la conversación
    pregunta_original: str                    # texto del usuario sin procesar
    categoria_detectada: str                  # ej: "smartphones", "audio"
    tipo_analisis: str                        # "tendencia" | "comparacion" | "oportunidad" | "general"
    respuesta_final: str                      # respuesta construida por el nodo especialista


# ─── CONSTRUCCIÓN DEL LLM (sin herramientas, para clasificar) ─

def _get_llm(temperature: float = 0.5):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=temperature,
            max_tokens=int(os.getenv("MAX_TOKENS", "1500")),
        )
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=temperature,
    )


# ─── NODO 1: CLASIFICADOR ────────────────────────────────────
# Usa temperature=0.0 para ser determinista al clasificar.

def nodo_clasificar(state: TrendState) -> dict:
    """
    Clasifica la pregunta en una categoría de producto y un tipo
    de análisis. Usa temperatura 0 para máxima consistencia.
    """
    llm_clasificador = _get_llm(temperature=0.0)

    prompt_clasificacion = f"""Clasifica la siguiente pregunta sobre electrónica de consumo.

Pregunta: "{state['pregunta_original']}"

Responde EXACTAMENTE con este formato JSON (sin markdown, sin explicaciones):
{{
  "categoria": "<una de: smartphones | audio | wearables | computadores | gaming | hogar_inteligente | tablets | camaras | consulta_general>",
  "tipo_analisis": "<una de: tendencia | comparacion | oportunidad | general>"
}}

Reglas de clasificación:
- tipo "tendencia": preguntas sobre crecimiento, cuota de mercado, qué está de moda
- tipo "comparacion": preguntas que comparan dos productos, marcas o categorías
- tipo "oportunidad": preguntas sobre negocio, invertir, vender, entrar al mercado
- tipo "general": saludos, preguntas fuera del dominio de electrónica, preguntas ambiguas
"""

    respuesta = llm_clasificador.invoke([HumanMessage(content=prompt_clasificacion)])

    # Extraemos el JSON de la respuesta
    import json, re
    texto = respuesta.content.strip()
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        try:
            datos = json.loads(match.group())
            return {
                "categoria_detectada": datos.get("categoria", "consulta_general"),
                "tipo_analisis": datos.get("tipo_analisis", "general"),
            }
        except json.JSONDecodeError:
            pass

    # Fallback si el LLM no devuelve JSON válido
    return {"categoria_detectada": "consulta_general", "tipo_analisis": "general"}


# ─── ROUTER CONDICIONAL ──────────────────────────────────────
# LangGraph llama a esta función para decidir el siguiente nodo.

def router(state: TrendState) -> str:
    """Devuelve el nombre del nodo especialista según tipo_analisis."""
    tipo = state.get("tipo_analisis", "general")
    rutas = {
        "tendencia": "nodo_tendencia",
        "comparacion": "nodo_comparacion",
        "oportunidad": "nodo_oportunidad",
        "general": "nodo_general",
    }
    return rutas.get(tipo, "nodo_general")


# ─── NODO 2: ANALISTA DE TENDENCIAS ─────────────────────────

def nodo_tendencia(state: TrendState) -> dict:
    """Especialista en tendencias de mercado y crecimiento."""
    llm = _get_llm()
    system = SystemMessage(content="""Eres un analista de tendencias de mercado en electrónica de consumo.
Tu especialidad: interpretar datos de crecimiento, cuota de mercado y momentum de categorías.
Responde con datos concretos: porcentajes YoY, tamaño de mercado en USD, marcas líderes.
Siempre menciona el período de referencia (2024-2025). Responde en español.""")

    respuesta = llm.invoke([system, HumanMessage(content=state["pregunta_original"])])
    return {"respuesta_final": respuesta.content}


# ─── NODO 3: ANALISTA DE COMPARACIONES ──────────────────────

def nodo_comparacion(state: TrendState) -> dict:
    """Especialista en comparar productos, marcas y categorías."""
    llm = _get_llm()
    system = SystemMessage(content="""Eres un analista comparativo de productos electrónicos.
Tu especialidad: contrastar dos opciones con datos de mercado objetivos.
Estructura tu respuesta en: criterio → comparación → veredicto claro.
Usa tablas o listas cuando faciliten la comprensión. Responde en español.""")

    respuesta = llm.invoke([system, HumanMessage(content=state["pregunta_original"])])
    return {"respuesta_final": respuesta.content}


# ─── NODO 4: ANALISTA DE OPORTUNIDADES ──────────────────────

def nodo_oportunidad(state: TrendState) -> dict:
    """Especialista en identificar oportunidades de negocio."""
    llm = _get_llm()
    system = SystemMessage(content="""Eres un analista de oportunidades de negocio en electrónica de consumo.
Tu especialidad: evaluar segmentos para emprendedores e inversores.
Siempre menciona: nivel de competencia, barreras de entrada, precio objetivo y recomendación accionable.
Sé directo: ¿es una buena oportunidad o no, y por qué? Responde en español.""")

    respuesta = llm.invoke([system, HumanMessage(content=state["pregunta_original"])])
    return {"respuesta_final": respuesta.content}


# ─── NODO 5: RESPUESTA GENERAL ──────────────────────────────

def nodo_general(state: TrendState) -> dict:
    """Maneja consultas generales o fuera del dominio especializado."""
    llm = _get_llm()
    system = SystemMessage(content="""Eres TrendScope, asistente de análisis de tendencias en electrónica de consumo.
Si la pregunta está fuera de tu dominio, indícalo amablemente y sugiere qué tipo de preguntas puedes responder.
Ejemplos de preguntas que SÍ puedes responder:
- ¿Cuál es la tendencia en smartwatches para 2025?
- ¿Conviene invertir en el segmento de earbuds gaming?
- ¿Cuáles son las marcas líderes en laptops?
Responde en español.""")

    respuesta = llm.invoke([system, HumanMessage(content=state["pregunta_original"])])
    return {"respuesta_final": respuesta.content}


# ─── CONSTRUCCIÓN DEL GRAFO ──────────────────────────────────

def build_trend_graph():
    """
    Ensambla el StateGraph con todos los nodos y las aristas
    condicionales. Devuelve el grafo compilado listo para invocar.
    """
    builder = StateGraph(TrendState)

    # Registrar nodos
    builder.add_node("nodo_clasificar", nodo_clasificar)
    builder.add_node("nodo_tendencia", nodo_tendencia)
    builder.add_node("nodo_comparacion", nodo_comparacion)
    builder.add_node("nodo_oportunidad", nodo_oportunidad)
    builder.add_node("nodo_general", nodo_general)

    # Aristas: flujo principal
    builder.add_edge(START, "nodo_clasificar")

    # Arista condicional: el router decide el nodo especialista
    builder.add_conditional_edges(
        "nodo_clasificar",
        router,
        {
            "nodo_tendencia": "nodo_tendencia",
            "nodo_comparacion": "nodo_comparacion",
            "nodo_oportunidad": "nodo_oportunidad",
            "nodo_general": "nodo_general",
        },
    )

    # Todos los nodos especialistas terminan en END
    for nodo in ["nodo_tendencia", "nodo_comparacion", "nodo_oportunidad", "nodo_general"]:
        builder.add_edge(nodo, END)

    return builder.compile()


# Instancia del grafo (se importa en las rutas de FastAPI)
trend_graph = build_trend_graph()


def analizar_con_grafo(pregunta: str) -> dict:
    """
    Función de conveniencia: recibe una pregunta, ejecuta el grafo
    y devuelve la respuesta final con metadatos de clasificación.
    """
    estado_inicial: TrendState = {
        "mensajes": [HumanMessage(content=pregunta)],
        "pregunta_original": pregunta,
        "categoria_detectada": "",
        "tipo_analisis": "",
        "respuesta_final": "",
    }

    resultado = trend_graph.invoke(estado_inicial)

    return {
        "respuesta": resultado["respuesta_final"],
        "categoria": resultado["categoria_detectada"],
        "tipo_analisis": resultado["tipo_analisis"],
    }
