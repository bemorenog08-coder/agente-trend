# TrendScope — Agente de IA para Análisis de Tendencias en Electrónica

**TrendScope** es una API conversacional que responde preguntas sobre el mercado de electrónica de consumo: qué categorías crecen, qué marcas dominan, dónde hay oportunidades de negocio y cómo comparar productos. Está construida con LangChain, LangGraph y FastAPI.

---

## 1. ¿Qué es TrendScope?

Es un agente de IA que actúa como **analista de mercado**. Le puedes preguntar en español cosas como:

- *"¿Qué tan rápido están creciendo los earbuds en 2025?"*
- *"¿Conviene entrar al segmento de smartwatches de salud?"*
- *"Compara el mercado de gaming vs hogar inteligente"*

El agente usa herramientas internas para buscar datos de mercado, comparar productos, analizar oportunidades y hacer cálculos. Recuerda la conversación dentro de una sesión (como un chat normal).

---

## 2. Requisitos previos

| Requisito | Versión mínima | Dónde obtenerlo |
|---|---|---|
| Python | 3.11+ | https://python.org/downloads |
| pip | incluido con Python | — |
| Cuenta Groq (gratis) | — | https://console.groq.com |
| API Key de Groq | — | Panel de Groq → "API Keys" → "Create API Key" |

> **¿Por qué Groq?** Groq ofrece un nivel gratuito generoso (~14,400 solicitudes/día con el modelo llama-3.3-70b-versatile). No necesitas tarjeta de crédito para empezar.

> **Alternativa local:** si tienes Ollama instalado (`ollama pull llama3.2`), puedes usar el agente sin internet ni API Key. Configura `LLM_PROVIDER=ollama` en tu `.env`.

---

## 3. Instalación paso a paso

### Paso 1: Clona o descarga el proyecto

```bash
git clone https://github.com/tu-usuario/trendscope.git
cd trendscope
```

Si descargaste un ZIP, extráelo y abre una terminal dentro de la carpeta `trendscope/`.

### Paso 2: Crea un entorno virtual

```bash
# En Windows
python -m venv .venv
.venv\Scripts\activate

# En macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Cuando el entorno está activo, verás `(.venv)` al inicio de tu línea de comandos.

### Paso 3: Instala las dependencias

```bash
pip install -r requirements.txt
```

Esto instala LangChain, LangGraph, FastAPI, Uvicorn y todo lo necesario (~2-3 minutos).

### Paso 4: Configura tu archivo `.env`

```bash
# Copia el ejemplo
cp .env.example .env   # en macOS/Linux
copy .env.example .env  # en Windows
```

Abre `.env` con cualquier editor de texto y reemplaza `tu_api_key_aqui` con tu API Key real de Groq:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
```

Guarda el archivo. **Nunca subas `.env` a GitHub** — está en `.gitignore` por esa razón.

---

## 4. Cómo arrancar el servidor

```bash
uvicorn main:app --reload
```

Cuando el servidor esté listo verás esto en la consola:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Application startup complete.
```

Abre tu navegador en **http://localhost:8000/docs** para ver la documentación interactiva (Swagger UI).

> El flag `--reload` hace que el servidor se reinicie automáticamente cuando editas un archivo. Útil en desarrollo; quítalo en producción.

---

## 5. Cómo usar la API

### Endpoint: `GET /` — Info de la API

```bash
curl http://localhost:8000/
```

```python
import requests
r = requests.get("http://localhost:8000/")
print(r.json())
```

---

### Endpoint: `GET /health` — Estado del servicio

```bash
curl http://localhost:8000/health
```

```python
r = requests.get("http://localhost:8000/health")
print(r.json())
# → {"status": "ok", "agente": "TrendScope", "proveedor": "groq", ...}
```

---

### Endpoint: `GET /health/detail` — Estado detallado

```bash
curl http://localhost:8000/health/detail
```

```python
r = requests.get("http://localhost:8000/health/detail")
print(r.json())
# Incluye modelo activo y lista de herramientas disponibles
```

---

### Endpoint: `POST /chat` — Conversación con memoria

Este es el endpoint principal. El campo `session_id` identifica tu conversación: mensajes con el mismo `session_id` se recuerdan entre sí.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "¿Qué tan rápido crece el mercado de wearables?", "session_id": "usuario-1"}'
```

```python
import requests

BASE = "http://localhost:8000"
SESSION = "mi-sesion-demo"

# Primera pregunta
r = requests.post(f"{BASE}/chat", json={
    "mensaje": "¿Qué tan rápido crece el mercado de wearables?",
    "session_id": SESSION,
})
print(r.json()["respuesta"])

# Segunda pregunta — el agente recuerda el contexto
r = requests.post(f"{BASE}/chat", json={
    "mensaje": "¿Y cuáles son las marcas líderes en ese segmento?",
    "session_id": SESSION,
})
print(r.json()["respuesta"])
```

**Respuesta esperada:**
```json
{
  "respuesta": "El mercado de wearables creció un 14.8% YoY en 2024...",
  "session_id": "mi-sesion-demo",
  "timestamp": "2025-01-15T10:23:45",
  "modelo": "llama-3.3-70b-versatile"
}
```

---

### Endpoint: `POST /analisis` — Análisis directo de segmento

Usa el grafo LangGraph para clasificar y analizar automáticamente un segmento.

```bash
curl -X POST http://localhost:8000/analisis \
  -H "Content-Type: application/json" \
  -d '{"segmento": "earbuds gaming bajo costo", "session_id": "analisis-1"}'
```

```python
r = requests.post(f"{BASE}/analisis", json={
    "segmento": "earbuds gaming bajo costo",
    "contexto": "Quiero importar desde China y vender en Latinoamérica",
    "session_id": "analisis-1",
})
print(r.json()["resultado"])
```

---

### Endpoint: `DELETE /chat/{session_id}` — Borrar historial

```bash
curl -X DELETE http://localhost:8000/chat/mi-sesion-demo
```

```python
r = requests.delete(f"{BASE}/chat/mi-sesion-demo")
print(r.json())
# → {"mensaje": "Historial de sesión 'mi-sesion-demo' eliminado.", ...}
```

---

## 6. Ejemplos de preguntas que TrendScope responde bien

1. *"¿Cuál es la tendencia en el mercado de smartphones para 2025?"*
2. *"¿Cuánto vale el mercado global de audífonos y quiénes lideran?"*
3. *"Compara el mercado de gaming vs wearables: ¿cuál tiene mayor crecimiento?"*
4. *"¿Conviene entrar al segmento de parlantes portátiles con marca propia?"*
5. *"¿Cuánto debería costar un smartwatch de gama media?"*
6. *"¿Qué tecnología está impulsando el crecimiento en laptops en 2025?"*
7. *"¿Qué tan competido está el segmento de tablets para educación?"*
8. *"Si el mercado de hogar inteligente es de 138,000 millones USD y crece 18%, ¿cuánto sumará en 2 años?"*
9. *"¿Cuáles son las barreras de entrada para vender earbuds gaming online?"*
10. *"¿El mercado de cámaras está creciendo o decreciendo? ¿Qué sub-segmento es la excepción?"*
11. *"Dame el rango de precios para laptops en gama media vs premium"*
12. *"¿Qué protocolo está unificando los dispositivos de hogar inteligente en 2024-2025?"*

---

## 7. Cómo desplegar en Railway

Railway es una plataforma que hospeda tu API gratis (con límites) y la hace accesible desde internet.

### Paso 1: Crea una cuenta en Railway

Ve a **https://railway.app** y regístrate (puedes usar tu cuenta de GitHub).

### Paso 2: Conecta tu repositorio de GitHub

1. Haz push de tu proyecto a un repositorio de GitHub (sin `.env`, solo `.env.example`).
2. En Railway, haz clic en **"New Project"** → **"Deploy from GitHub repo"**.
3. Selecciona tu repositorio `trendscope`.

### Paso 3: Configura las variables de entorno

En el panel de Railway, ve a tu servicio → **"Variables"** y agrega:

| Variable | Valor |
|---|---|
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | tu API Key real |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `API_HOST` | `0.0.0.0` |
| `API_PORT` | `8000` |
| `API_DEBUG` | `False` |

### Paso 4: Configura el comando de arranque

En **"Settings"** → **"Start Command"**:

```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

> Railway asigna el puerto automáticamente via `$PORT`. Si usas `API_PORT=8000` hardcodeado puede haber conflicto.

### Paso 5: Despliega

Railway detectará automáticamente que es un proyecto Python con `requirements.txt` e instalará las dependencias. El despliegue toma 1-2 minutos.

### Paso 6: Obtén tu URL pública

Una vez desplegado, Railway te dará una URL como:
```
https://trendscope-production-xxxx.up.railway.app
```

Pruébala:
```bash
curl https://trendscope-production-xxxx.up.railway.app/health
```

---

## 8. Estructura del proyecto

```
trendscope/
├── .env.example        # Plantilla de variables de entorno (sube a GitHub)
├── .env                # Tus valores reales (NO subir a GitHub)
├── .gitignore          # Archivos excluidos de git
├── requirements.txt    # Dependencias de Python
├── main.py             # Punto de entrada: crea la app FastAPI y registra las rutas
├── README.md           # Este archivo
│
├── core/
│   └── agent_core.py   # LLM + herramientas + memoria por sesión (patrón Sesión 2-3)
│
├── models/
│   └── schemas.py      # Modelos Pydantic: qué recibe y qué devuelve cada endpoint
│
├── routes/
│   ├── chat.py         # POST /chat y DELETE /chat/{session_id}
│   ├── analisis.py     # POST /analisis (usa el grafo LangGraph)
│   └── health.py       # GET /health y GET /health/detail
│
├── tools/
│   └── market_tools.py # Las 5 herramientas @tool que el agente puede usar
│
└── graph/
    └── trend_graph.py  # Grafo condicional LangGraph (patrón Sesión 4)
```

**Cómo se conectan los archivos:**

```
main.py
  ├── importa routes/chat.py       → usa core/agent_core.py → usa tools/market_tools.py
  ├── importa routes/analisis.py   → usa graph/trend_graph.py
  └── importa routes/health.py     → usa tools/market_tools.py (para listar herramientas)

core/agent_core.py
  └── importa tools/market_tools.py (la lista TOOLS)

routes/chat.py y routes/analisis.py
  └── usan models/schemas.py para validar request y response
```

---

## 9. Cómo personalizar TrendScope

### Cambiar el dominio de análisis

Edita `core/agent_core.py` → `SYSTEM_PROMPT`. Cambia "electrónica de consumo" por tu industria (moda, alimentos, salud...).

### Agregar nuevas herramientas

1. Abre `tools/market_tools.py`.
2. Crea una nueva función con el decorador `@tool`.
3. Agrégala a la lista `TOOLS` al final del archivo.
4. El agente la usará automáticamente en la siguiente consulta.

### Cambiar el modelo de IA

En tu `.env`, cambia `GROQ_MODEL` por cualquier modelo disponible en Groq:
- `llama-3.3-70b-versatile` (más capaz, recomendado)
- `llama-3.1-8b-instant` (más rápido, nivel gratuito más alto)
- `mixtral-8x7b-32768` (ventana de contexto grande)

### Cambiar a Ollama (IA 100% local)

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

Asegúrate de tener Ollama corriendo: `ollama serve` y el modelo descargado: `ollama pull llama3.2`.

### Agregar categorías al grafo

Edita `graph/trend_graph.py` → función `router()`. Agrega una nueva clave en el diccionario `rutas` y crea el nodo correspondiente.

---

## 10. Solución de problemas comunes

### ❌ `ModuleNotFoundError: No module named 'langchain'`

**Causa:** el entorno virtual no está activado o las dependencias no están instaladas.

**Solución:**
```bash
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

### ❌ `AuthenticationError: invalid api key`

**Causa:** la API Key de Groq es incorrecta o no está en `.env`.

**Solución:**
1. Verifica que el archivo `.env` existe (no solo `.env.example`).
2. Confirma que `GROQ_API_KEY` empieza con `gsk_`.
3. Genera una nueva key en https://console.groq.com → API Keys.

---

### ❌ `ConnectionError` al usar Ollama

**Causa:** el servidor de Ollama no está corriendo.

**Solución:**
```bash
ollama serve          # arranca Ollama en segundo plano
ollama pull llama3.2  # descarga el modelo si no lo tienes
```

---

### ❌ `Address already in use` al arrancar uvicorn

**Causa:** el puerto 8000 ya está en uso por otro proceso.

**Solución:**
```bash
uvicorn main:app --reload --port 8001
```

---

### ❌ El agente responde en inglés

**Causa:** el SYSTEM_PROMPT no se está inyectando correctamente.

**Solución:** verifica que `core/agent_core.py` tiene `SYSTEM_PROMPT` con la instrucción `Responde en español` y que el `ChatPromptTemplate` lo incluye en la posición `("system", SYSTEM_PROMPT)`.

---

### ❌ Railway falla con `ModuleNotFoundError`

**Causa:** `requirements.txt` no está en la raíz del proyecto o tiene errores de formato.

**Solución:** asegúrate de que el archivo `requirements.txt` está en la carpeta `trendscope/` (la raíz que subes a GitHub) y que cada dependencia está en su propia línea sin espacios extras.

---

## Licencia

MIT — úsalo, modifícalo y despliégalo libremente.
