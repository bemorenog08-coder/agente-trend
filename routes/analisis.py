# ============================================================
# analisis.py — Endpoint de análisis directo con LangGraph
# En lugar de conversación libre, el usuario especifica un
# segmento y el grafo enruta al nodo especialista adecuado.
# ============================================================

from fastapi import APIRouter, HTTPException
from models.schemas import AnalisisRequest, AnalisisResponse
from graph.trend_graph import analizar_con_grafo

router = APIRouter(prefix="/analisis", tags=["Análisis"])


@router.post("/", response_model=AnalisisResponse)
async def analisis_segmento(request: AnalisisRequest):
    """
    Analiza un segmento de mercado usando el grafo LangGraph.
    El grafo clasifica automáticamente la pregunta y la dirige
    al nodo especialista (tendencia / comparación / oportunidad).
    """
    # Construimos la pregunta combinando segmento y contexto opcional
    pregunta = f"Analiza el segmento: {request.segmento}"
    if request.contexto:
        pregunta += f". Contexto adicional: {request.contexto}"

    try:
        resultado = analizar_con_grafo(pregunta)
        return AnalisisResponse(
            resultado=resultado["respuesta"],
            segmento=request.segmento,
            session_id=request.session_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en el análisis: {exc}") from exc
