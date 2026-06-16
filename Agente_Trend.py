# ============================================================
# main.py — Punto de entrada de la API Agente_Trend
# Arranca con: uvicorn main:app --reload
# Patrón: Sesión 5 del seminario de Agentes de IA.
# ============================================================

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.chat import router as chat_router
from routes.analisis import router as analisis_router
from routes.health import router as health_router

load_dotenv()

# ─── METADATA DE LA API ──────────────────────────────────────
# ✏️ MODIFICA AQUÍ: cambia título y descripción para tu dominio

app = FastAPI(
    title="Agente_Trend API — Análisis de Tendencias en Electrónica",
    description="""
**Agente_Trend** es un agente de IA especializado en tendencias del mercado de electrónica de consumo (2024-2025).

## Endpoints disponibles

### 💬 Chat (con memoria)
- `POST /chat` — Conversa con el agente. Incluye `session_id` para mantener contexto entre mensajes.
- `DELETE /chat/{session_id}` — Borra el historial de una sesión.

### 📊 Análisis directo
- `POST /analisis` — Análisis de un segmento de mercado usando el grafo LangGraph especializado.

### 🏥 Estado del servicio
- `GET /health` — Verificación básica (útil para Railway health checks).
- `GET /health/detail` — Estado detallado con modelo activo y herramientas disponibles.

## Categorías soportadas
`smartphones` · `audio` · `wearables` · `computadores` · `gaming` · `hogar_inteligente` · `tablets` · `camaras`

## Herramientas del agente
El agente puede buscar tendencias, comparar productos, analizar oportunidades, consultar precios de referencia y hacer cálculos de mercado.
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ───────────────────────────────────────────────────
# allow_origins=["*"] permite acceso desde cualquier frontend.
# ✏️ MODIFICA AQUÍ: restringe a tu dominio en producción si es necesario.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── RUTAS ──────────────────────────────────────────────────

app.include_router(chat_router)
app.include_router(analisis_router)
app.include_router(health_router)


# ─── RUTA RAÍZ ──────────────────────────────────────────────

@app.get("/", tags=["Info"])
async def root():
    """Información básica de la API."""
    return {
        "nombre": os.getenv("AGENT_NAME", "Agente_Trend"),
        "descripcion": "Agente de IA para análisis de tendencias en electrónica de consumo",
        "version": "1.0.0",
        "proveedor_llm": os.getenv("LLM_PROVIDER", "groq"),
        "docs": "/docs",
        "health": "/health",
    }


# ─── ARRANQUE DIRECTO ────────────────────────────────────────
# Permite ejecutar: python main.py (además de uvicorn main:app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("API_DEBUG", "True").lower() == "true",
    )
