# ============================================================
# market_tools.py — Herramientas de mercado para el agente
# Cada función decorada con @tool se convierte en una
# "habilidad" que el LLM puede invocar cuando lo necesite.
# Los datos son simulados pero realistas (2024-2025).
# ============================================================

import math
from langchain_core.tools import tool


# ─── BASE DE DATOS DE MERCADO SIMULADA ──────────────────────
# ✏️ MODIFICA AQUÍ: actualiza o amplía estos datos cada trimestre

_DATOS_MERCADO = {
    "smartphones": {
        "crecimiento_yoy": "+6.2%",
        "marcas_lideres": ["Samsung (22%)", "Apple (18%)", "Xiaomi (13%)", "OPPO (10%)", "Vivo (8%)"],
        "precio_promedio_usd": 420,
        "segmento_mayor_demanda": "Gama media ($200–$500) — representa el 54% de las ventas globales",
        "tendencia_clave": "Cámaras de 200 MP y chips de IA on-device dominan la narrativa 2024-2025",
        "mercado_total_musd": 484_000,
    },
    "audio": {
        "crecimiento_yoy": "+11.4%",
        "marcas_lideres": ["Sony (19%)", "Samsung/JBL (15%)", "Apple/Beats (14%)", "Bose (11%)", "Jabra (7%)"],
        "precio_promedio_usd": 95,
        "segmento_mayor_demanda": "True Wireless Stereo (TWS) — earbuds representan el 61% del volumen",
        "tendencia_clave": "ANC activa en gama media, lossless inalámbrico (aptX Lossless, LDAC) y audio espacial",
        "mercado_total_musd": 62_000,
    },
    "wearables": {
        "crecimiento_yoy": "+14.8%",
        "marcas_lideres": ["Apple Watch (27%)", "Samsung Galaxy Watch (12%)", "Fitbit/Google (9%)", "Garmin (8%)", "Xiaomi Band (7%)"],
        "precio_promedio_usd": 210,
        "segmento_mayor_demanda": "Smartwatches de salud avanzada ($150–$400) — monitoreo ECG y glucosa no invasiva",
        "tendencia_clave": "Sensores de salud clínica (presión arterial, oxígeno en sangre) abriendo mercado médico",
        "mercado_total_musd": 95_000,
    },
    "computadores": {
        "crecimiento_yoy": "+3.8%",
        "marcas_lideres": ["Lenovo (23%)", "HP (21%)", "Dell (17%)", "Apple (9%)", "ASUS (7%)"],
        "precio_promedio_usd": 780,
        "segmento_mayor_demanda": "Laptops ultradelgadas con NPU para IA local ($700–$1200) — segmento Copilot+ PC",
        "tendencia_clave": "Chips con NPU integrada (Snapdragon X, Intel Core Ultra, Apple M4) para IA on-device",
        "mercado_total_musd": 210_000,
    },
    "gaming": {
        "crecimiento_yoy": "+8.6%",
        "marcas_lideres": ["Sony PS5 (31%)", "Nintendo Switch (22%)", "Microsoft Xbox (18%)", "Valve Steam Deck (5%)", "ASUS ROG (4%)"],
        "precio_promedio_usd": 340,
        "segmento_mayor_demanda": "Periféricos gaming (teclados, ratones, headsets) — margen 3× mayor que consolas",
        "tendencia_clave": "Cloud gaming creciendo 28% YoY; handheld gaming PC (Steam Deck, ROG Ally) explosión en 2024",
        "mercado_total_musd": 227_000,
    },
    "hogar_inteligente": {
        "crecimiento_yoy": "+18.2%",
        "marcas_lideres": ["Amazon Echo (21%)", "Google Nest (18%)", "Apple HomeKit (12%)", "Samsung SmartThings (10%)", "Xiaomi Mi Home (9%)"],
        "precio_promedio_usd": 65,
        "segmento_mayor_demanda": "Seguridad del hogar (cámaras, cerraduras, alarmas) — 38% del volumen total",
        "tendencia_clave": "Protocolo Matter unificando ecosistemas; energía solar + almacenamiento integrado al hogar inteligente",
        "mercado_total_musd": 138_000,
    },
    "tablets": {
        "crecimiento_yoy": "+5.1%",
        "marcas_lideres": ["Apple iPad (37%)", "Samsung Galaxy Tab (22%)", "Amazon Fire (11%)", "Lenovo Tab (9%)", "Microsoft Surface (6%)"],
        "precio_promedio_usd": 490,
        "segmento_mayor_demanda": "Tablets premium para creadores ($600–$1200) — con stylus y teclado",
        "tendencia_clave": "Tablets sustituyendo laptops en educación y trabajo creativo; OLED en gama media desde 2024",
        "mercado_total_musd": 52_000,
    },
    "camaras": {
        "crecimiento_yoy": "-2.1%",
        "marcas_lideres": ["Sony (29%)", "Canon (27%)", "Nikon (16%)", "Fujifilm (9%)", "Panasonic (6%)"],
        "precio_promedio_usd": 1_100,
        "segmento_mayor_demanda": "Mirrorless full-frame ($1500–$3500) — único segmento con crecimiento positivo (+12%)",
        "tendencia_clave": "Smartphones erosionan mercado compacto; mirrorless y cámaras de video profesional son el refugio",
        "mercado_total_musd": 8_500,
    },
}

_PRECIOS_REFERENCIA = {
    "smartphones": {"entrada": "$80–$200", "gama_media": "$200–$500", "premium": "$500–$1600"},
    "earbuds": {"entrada": "$15–$50", "gama_media": "$50–$150", "premium": "$150–$350"},
    "audifonos": {"entrada": "$20–$60", "gama_media": "$60–$200", "premium": "$200–$500"},
    "parlantes": {"entrada": "$25–$80", "gama_media": "$80–$300", "premium": "$300–$800"},
    "smartwatch": {"entrada": "$30–$100", "gama_media": "$100–$300", "premium": "$300–$1000"},
    "laptop": {"entrada": "$300–$600", "gama_media": "$600–$1200", "premium": "$1200–$4000"},
    "tablet": {"entrada": "$100–$250", "gama_media": "$250–$600", "premium": "$600–$2000"},
    "consola": {"entrada": "$150–$200 (portátil)", "gama_media": "$300–$400", "premium": "$500–$700"},
    "camara": {"entrada": "$200–$500", "gama_media": "$500–$1500", "premium": "$1500–$6000"},
    "router_wifi": {"entrada": "$30–$60", "gama_media": "$60–$180", "premium": "$180–$500"},
}


# ─── HERRAMIENTA 1: TENDENCIA POR CATEGORÍA ─────────────────

@tool
def buscar_tendencia_categoria(categoria: str) -> str:
    """
    Devuelve datos de tendencia de mercado para una categoría
    de electrónica de consumo (2024-2025).
    Categorías válidas: smartphones, audio, wearables, computadores,
    gaming, hogar_inteligente, tablets, camaras.
    """
    categoria_lower = categoria.lower().strip()

    # Mapeo de sinónimos para flexibilidad
    sinonimos = {
        "audífonos": "audio", "audifonos": "audio", "earbuds": "audio",
        "parlantes": "audio", "auriculares": "audio",
        "smartwatch": "wearables", "reloj inteligente": "wearables",
        "fitness tracker": "wearables",
        "laptop": "computadores", "laptops": "computadores",
        "pc": "computadores", "notebook": "computadores",
        "consolas": "gaming", "videojuegos": "gaming",
        "smart home": "hogar_inteligente", "iot": "hogar_inteligente",
        "cámara": "camaras", "camara": "camaras",
    }

    clave = sinonimos.get(categoria_lower, categoria_lower)
    datos = _DATOS_MERCADO.get(clave)

    if not datos:
        disponibles = ", ".join(_DATOS_MERCADO.keys())
        return (
            f"No tengo datos específicos para '{categoria}'. "
            f"Categorías disponibles: {disponibles}."
        )

    marcas = "\n  • ".join(datos["marcas_lideres"])
    return f"""
📊 TENDENCIA DE MERCADO — {categoria.upper()} (2024-2025)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Crecimiento YoY:       {datos['crecimiento_yoy']}
Mercado total:         ${datos['mercado_total_musd']:,} M USD
Precio promedio:       ${datos['precio_promedio_usd']} USD

Marcas líderes (cuota global):
  • {marcas}

Mayor demanda:         {datos['segmento_mayor_demanda']}
Tendencia clave 2025:  {datos['tendencia_clave']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fuente: datos simulados TrendScope (ref. Q4 2024 – Q1 2025)
"""


# ─── HERRAMIENTA 2: COMPARACIÓN DE PRODUCTOS ────────────────

@tool
def comparar_productos(producto_a: str, producto_b: str) -> str:
    """
    Compara dos categorías o productos en términos de mercado:
    demanda, precio y tendencia de crecimiento.
    """
    def _buscar(nombre: str):
        sinonimos = {
            "audio": "audio", "audífonos": "audio", "earbuds": "audio",
            "wearables": "wearables", "smartwatch": "wearables",
            "gaming": "gaming", "videojuegos": "gaming",
            "computadores": "computadores", "laptops": "computadores",
            "hogar_inteligente": "hogar_inteligente", "smart home": "hogar_inteligente",
        }
        clave = sinonimos.get(nombre.lower(), nombre.lower())
        return clave, _DATOS_MERCADO.get(clave)

    clave_a, datos_a = _buscar(producto_a)
    clave_b, datos_b = _buscar(producto_b)

    if not datos_a or not datos_b:
        faltante = producto_a if not datos_a else producto_b
        return f"No tengo datos de mercado para '{faltante}'. Prueba con: {', '.join(_DATOS_MERCADO.keys())}."

    # Determinamos cuál tiene mayor demanda por tamaño de mercado
    ganador_mercado = producto_a if datos_a["mercado_total_musd"] > datos_b["mercado_total_musd"] else producto_b
    diferencia_mercado = abs(datos_a["mercado_total_musd"] - datos_b["mercado_total_musd"])

    # Crecimiento: extraemos el número del string "+X.X%"
    crec_a = float(datos_a["crecimiento_yoy"].replace("%", "").replace("+", ""))
    crec_b = float(datos_b["crecimiento_yoy"].replace("%", "").replace("+", ""))
    ganador_crec = producto_a if crec_a > crec_b else producto_b

    return f"""
⚖️ COMPARACIÓN DE MERCADO: {producto_a.upper()} vs {producto_b.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TAMAÑO DE MERCADO
  {producto_a}: ${datos_a['mercado_total_musd']:,} M USD
  {producto_b}: ${datos_b['mercado_total_musd']:,} M USD
  → Mayor mercado: {ganador_mercado} (diferencia de ${diferencia_mercado:,} M USD)

CRECIMIENTO YoY
  {producto_a}: {datos_a['crecimiento_yoy']}
  {producto_b}: {datos_b['crecimiento_yoy']}
  → Crece más rápido: {ganador_crec}

PRECIO PROMEDIO
  {producto_a}: ${datos_a['precio_promedio_usd']} USD
  {producto_b}: ${datos_b['precio_promedio_usd']} USD

SEGMENTO ESTRELLA
  {producto_a}: {datos_a['segmento_mayor_demanda']}
  {producto_b}: {datos_b['segmento_mayor_demanda']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ─── HERRAMIENTA 3: ANÁLISIS DE OPORTUNIDAD ─────────────────

@tool
def analizar_oportunidad(segmento: str) -> str:
    """
    Analiza la oportunidad de negocio de un segmento específico
    del mercado de electrónica. Ej: 'earbuds gaming bajo costo',
    'smartwatch salud gama media', 'router WiFi 7'.
    """
    # ✏️ MODIFICA AQUÍ: añade más segmentos a este diccionario
    oportunidades = {
        "earbuds gaming": {
            "competencia": "Alta",
            "barrera_entrada": "Media — requiere certificación de baja latencia (<40ms) y micrófono boom desmontable",
            "crecimiento_segmento": "+22% YoY",
            "precio_objetivo": "$40–$90 USD",
            "recomendacion": "Nicho viable si te diferencias con micrófono desmontable y compatibilidad multiplataforma. Marcas como HyperX y SteelSeries dominan, pero hay espacio en precio < $50.",
        },
        "smartwatch salud": {
            "competencia": "Alta",
            "barrera_entrada": "Alta — sensores de precisión clínica requieren certificación FDA/CE y hardware especializado",
            "crecimiento_segmento": "+31% YoY (sub-segmento médico)",
            "precio_objetivo": "$150–$400 USD",
            "recomendacion": "Segmento de altísimo crecimiento pero dominado por Apple, Samsung y Garmin. Oportunidad real en nichos (atletas, tercera edad, B2B corporativo).",
        },
        "parlantes portátiles": {
            "competencia": "Alta",
            "barrera_entrada": "Baja-Media — manufactura accesible via ODM en China, diferenciación difícil",
            "crecimiento_segmento": "+9% YoY",
            "precio_objetivo": "$30–$120 USD",
            "recomendacion": "Mercado saturado en gama baja. Oportunidad en parlantes con energía solar o resistencia extrema (IP68 + resistencia a caídas) para uso outdoor.",
        },
        "router wifi": {
            "competencia": "Media",
            "barrera_entrada": "Alta — requiere certificaciones WiFi 6E/7, firmware robusto y soporte técnico 24/7",
            "crecimiento_segmento": "+16% YoY (WiFi 7)",
            "precio_objetivo": "$80–$300 USD",
            "recomendacion": "WiFi 7 es el punto de entrada para el siguiente ciclo de actualización masiva (2025-2027). Oportunidad para distribuidores y resellers B2B en PyMEs.",
        },
        "tablets educacion": {
            "competencia": "Media",
            "barrera_entrada": "Media — requiere acuerdos institucionales y software educativo certificado",
            "crecimiento_segmento": "+18% YoY (sector educativo)",
            "precio_objetivo": "$100–$250 USD",
            "recomendacion": "Licitaciones públicas y acuerdos con escuelas son la vía. Amazon Fire y Lenovo dominan precio bajo; hay espacio con propuesta de valor en contenido local.",
        },
    }

    # Buscar por palabras clave en el segmento ingresado
    segmento_lower = segmento.lower()
    resultado = None
    for clave, datos in oportunidades.items():
        if any(palabra in segmento_lower for palabra in clave.split()):
            resultado = (clave, datos)
            break

    if not resultado:
        # Análisis genérico cuando no hay datos específicos
        return f"""
💡 ANÁLISIS DE OPORTUNIDAD — {segmento.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
No tengo datos específicos para este segmento exacto.

Recomendación general para evaluar la oportunidad:
  1. Verifica el crecimiento YoY del mercado padre con buscar_tendencia_categoria
  2. Analiza si hay diferenciación posible (precio, característica única, canal)
  3. Evalúa barreras: patentes, certificaciones (FCC, CE), capital de manufactura
  4. Considera el modelo: ¿reventa, marca blanca, desarrollo propio o SaaS?

Segmentos con análisis detallado disponibles:
  earbuds gaming | smartwatch salud | parlantes portátiles | router wifi | tablets educacion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    clave, datos = resultado
    return f"""
💡 ANÁLISIS DE OPORTUNIDAD — {segmento.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nivel de competencia:   {datos['competencia']}
Barrera de entrada:     {datos['barrera_entrada']}
Crecimiento segmento:   {datos['crecimiento_segmento']}
Precio objetivo:        {datos['precio_objetivo']}

📌 Recomendación:
{datos['recomendacion']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Datos de referencia: Q4 2024 – Q1 2025
"""


# ─── HERRAMIENTA 4: PRECIOS DE REFERENCIA ───────────────────

@tool
def precio_referencia(producto: str) -> str:
    """
    Devuelve rangos de precio de referencia por tier (entrada,
    gama media, premium) para productos de electrónica de consumo.
    """
    producto_lower = producto.lower().strip()
    sinonimos = {
        "smartphone": "smartphones", "celular": "smartphones", "móvil": "smartphones",
        "audífono": "audifonos", "headphones": "audifonos", "over-ear": "audifonos",
        "earbud": "earbuds", "tws": "earbuds", "in-ear": "earbuds",
        "parlante": "parlantes", "speaker": "parlantes", "bocina": "parlantes",
        "reloj": "smartwatch", "smartwatch": "smartwatch", "wearable": "smartwatch",
        "laptop": "laptop", "portátil": "laptop", "notebook": "laptop",
        "tablet": "tablet", "ipad": "tablet",
        "consola": "consola", "playstation": "consola", "xbox": "consola",
        "cámara": "camara", "dslr": "camara", "mirrorless": "camara",
        "router": "router_wifi", "wifi": "router_wifi", "mesh": "router_wifi",
    }

    clave = sinonimos.get(producto_lower, producto_lower)
    precios = _PRECIOS_REFERENCIA.get(clave)

    if not precios:
        disponibles = ", ".join(_PRECIOS_REFERENCIA.keys())
        return (
            f"No tengo precios de referencia para '{producto}'. "
            f"Productos disponibles: {disponibles}."
        )

    return f"""
💰 PRECIOS DE REFERENCIA — {producto.upper()} (2024-2025)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Entrada (básico):   {precios['entrada']}
  Gama media:         {precios['gama_media']}
  Premium:            {precios['premium']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nota: precios en USD, referencia mercado global Q1 2025.
Precios locales varían por impuestos, logística e importación.
"""


# ─── HERRAMIENTA 5: CALCULADORA DE MERCADO ──────────────────

@tool
def calculadora(expresion: str) -> str:
    """
    Evalúa expresiones matemáticas para estimaciones de mercado.
    Soporta: +, -, *, /, **, sqrt, ceil, floor, log, pi, e.
    Ejemplo: '484000 * 0.062' para calcular crecimiento de mercado.
    """
    # Contexto seguro: sólo funciones matemáticas, sin acceso a builtins peligrosos
    contexto_seguro = {
        "__builtins__": {},
        "sqrt": math.sqrt,
        "ceil": math.ceil,
        "floor": math.floor,
        "log": math.log,
        "log10": math.log10,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
    }
    try:
        resultado = eval(expresion, contexto_seguro)  # noqa: S307
        return f"Resultado de '{expresion}' = {resultado:,.4f}".rstrip("0").rstrip(".")
    except ZeroDivisionError:
        return "Error: división por cero."
    except Exception as exc:
        return f"Error al evaluar '{expresion}': {exc}. Usa operadores válidos: +, -, *, /, **, sqrt(), log()."


# ─── HERRAMIENTA 6: GOOGLE TRENDS (DATOS REALES) ────────────

@tool
def tendencia_google(termino: str, periodo: str = "hoy 3-m") -> str:
    """
    Consulta Google Trends para obtener el nivel de interés real
    de un término de búsqueda en los últimos meses.
    Parámetros:
      termino: palabra o frase a buscar, ej: 'smartwatch', 'earbuds gaming'
      periodo: ventana de tiempo. Opciones:
               'hoy 1-m' (último mes),
               'hoy 3-m' (últimos 3 meses, por defecto),
               'hoy 12-m' (último año)
    Devuelve: promedio de interés (0-100), pico máximo y tendencia reciente.
    """
    try:
        from pytrends.request import TrendReq
        import pandas as pd

        pytrends = TrendReq(hl="es-419", tz=300, timeout=(10, 25))
        pytrends.build_payload(
            kw_list=[termino],
            cat=0,
            timeframe=periodo,
            geo="",       # mundial; cambia a "CO", "MX", "ES" para un país
            gprop="",
        )
        df = pytrends.interest_over_time()

        if df.empty or termino not in df.columns:
            return f"Google Trends no devolvió datos para '{termino}'. Intenta con un término más general."

        serie = df[termino]
        promedio = int(serie.mean())
        maximo = int(serie.max())
        ultimo = int(serie.iloc[-1])
        penultimo = int(serie.iloc[-2]) if len(serie) > 1 else ultimo
        tendencia = "↑ subiendo" if ultimo > penultimo else "↓ bajando" if ultimo < penultimo else "→ estable"

        # Fecha del pico
        fecha_pico = serie.idxmax().strftime("%b %Y")

        return f"""
🌐 GOOGLE TRENDS — "{termino}" ({periodo})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Interés promedio:   {promedio}/100
Pico máximo:        {maximo}/100 (en {fecha_pico})
Interés reciente:   {ultimo}/100 {tendencia}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Escala: 100 = máximo interés histórico en el período.
Fuente: Google Trends (datos en tiempo real)
"""
    except Exception as exc:
        return (
            f"Error consultando Google Trends para '{termino}': {exc}. "
            "Verifica tu conexión a internet o intenta con otro término."
        )


# Lista exportable de todas las herramientas (se importa en agent_core.py)
TOOLS = [
    buscar_tendencia_categoria,
    comparar_productos,
    analizar_oportunidad,
    precio_referencia,
    calculadora,
    tendencia_google,
]
