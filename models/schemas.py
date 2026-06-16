# ============================================================
# schemas.py — Modelos de datos (contratos de la API)
# Define qué recibe y qué devuelve cada endpoint.
# Pydantic valida automáticamente los tipos al recibir JSON.
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── CHAT ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Lo que el cliente envía al endpoint /chat."""
    mensaje: str = Field(..., description="Pregunta o mensaje del usuario")
    # ✏️ MODIFICA AQUÍ: cambia "default" por cualquier ID que identifique al usuario
    session_id: str = Field(default="default", description="ID único de la conversación")


class ChatResponse(BaseModel):
    """Lo que el servidor devuelve desde /chat."""
    respuesta: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    modelo: str


# ─── ANÁLISIS DIRECTO ────────────────────────────────────────

class AnalisisRequest(BaseModel):
    """Lo que el cliente envía al endpoint /analisis."""
    segmento: str = Field(..., description="Segmento a analizar, ej: 'audífonos gaming'")
    contexto: Optional[str] = Field(None, description="Contexto adicional opcional")
    session_id: str = Field(default="default")


class AnalisisResponse(BaseModel):
    """Lo que el servidor devuelve desde /analisis."""
    resultado: str
    segmento: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)


# ─── SALUD DEL SERVICIO ──────────────────────────────────────

class HealthResponse(BaseModel):
    """Respuesta del endpoint /health."""
    status: str
    agente: str
    proveedor: str
    version: str
    herramientas: list[str]
