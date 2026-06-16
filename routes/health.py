# ============================================================
# health.py — Endpoints de estado del servicio
# Permite a Railway (y a ti) verificar que la API está viva.
# ============================================================

import os
from fastapi import APIRouter
from models.schemas import HealthResponse
from tools.market_tools import TOOLS

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Estado básico del servicio."""
    return HealthResponse(
        status="ok",
        agente=os.getenv("AGENT_NAME", "TrendScope"),
        proveedor=os.getenv("LLM_PROVIDER", "groq"),
        version="1.0.0",
        herramientas=[t.name for t in TOOLS],
    )


@router.get("/detail", response_model=HealthResponse)
async def health_detail():
    """Estado detallado: incluye lista de herramientas activas y configuración."""
    return HealthResponse(
        status="ok",
        agente=os.getenv("AGENT_NAME", "TrendScope"),
        proveedor=f"{os.getenv('LLM_PROVIDER', 'groq')} / {os.getenv('GROQ_MODEL', os.getenv('OLLAMA_MODEL', 'desconocido'))}",
        version="1.0.0",
        herramientas=[f"{t.name}: {t.description[:60]}..." for t in TOOLS],
    )
