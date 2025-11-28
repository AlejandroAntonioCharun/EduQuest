# ─────────────────────────────────────────────────────────────
# 📦 IA SERVICE – Generación y retroalimentación con Google Gemini
# Compatible con google-genai >= 1.0.0
# ─────────────────────────────────────────────────────────────

from google import genai
from decouple import config
from typing import List, Dict
import json
import logging

# ─────────────────────────────────────────────────────────────
# 🔑 Configuración del cliente de Gemini
# ─────────────────────────────────────────────────────────────

# En tu archivo .env debe existir:
GEMINI_API_KEY= "AIzaSyBVe_ueEE5tfqYlcgQSFRzKT7i9Qmx_PVQ"
GEMINI_API_KEY = config("GEMINI_API_KEY", default="")

# Solo inicializamos el cliente si hay API key configurada para evitar crash en arranque
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

logging.basicConfig(level=logging.INFO)


# ─────────────────────────────────────────────────────────────
# 🧩 1. Generar preguntas de opción múltiple
# ─────────────────────────────────────────────────────────────
def generar_quiz_automatico(
    tema: str,
    cantidad_preguntas: int = 5,
    modelo: str = "gemini-2.0-flash"
) -> List[Dict]:
    """
    Genera un cuestionario educativo de opción múltiple sobre un tema dado.

    Args:
        tema: Tema principal (ej. "Matemáticas básicas")
        cantidad_preguntas: Número de preguntas a generar
        modelo: Modelo de Gemini a usar ("gemini-2.0-flash" o "gemini-2.0-pro")

    Returns:
        Lista de preguntas con formato:
        [
          {
            "pregunta": "...",
            "opciones": ["A", "B", "C", "D"],
            "respuesta_correcta": "...",
            "explicacion": "..."
          }
        ]
    """
    prompt = f"""
    Crea un cuestionario educativo sobre el tema "{tema}".
    Debe contener exactamente {cantidad_preguntas} preguntas de opción múltiple.
    Devuélvelo como JSON válido con esta estructura exacta:
    [
      {{
        "pregunta": "texto de la pregunta",
        "opciones": ["opción A", "opción B", "opción C", "opción D"],
        "respuesta_correcta": "texto exacto de la respuesta correcta",
        "explicacion": "explicación corta"
      }}
    ]
    No incluyas texto fuera del JSON.
    """

    try:
        if not client:
            return "Configura GEMINI_API_KEY para habilitar feedback con IA."

        response = client.models.generate_content(
            model=modelo,
            contents=prompt
        )

        content = response.text.strip("`").strip()
        if not content.startswith("["):
            content = content[content.find("["):]
        quiz_data = json.loads(content)

        logging.info(f"✅ Se generaron {len(quiz_data)} preguntas sobre '{tema}'.")
        return quiz_data

    except Exception as e:
        logging.error(f"❌ Error al generar el quiz: {e}")
        return []


# ─────────────────────────────────────────────────────────────
# 🧠 2. Generar retroalimentación personalizada
# ─────────────────────────────────────────────────────────────
def generar_explicacion(
    pregunta: str,
    respuesta_usuario: str,
    respuesta_correcta: str,
    modelo: str = "gemini-2.0-flash"
) -> str:
    """
    Genera retroalimentación educativa corta sobre una respuesta.
    """
    prompt = f"""
    Evalúa esta pregunta:
    Pregunta: {pregunta}
    Respuesta del usuario: {respuesta_usuario}
    Respuesta correcta: {respuesta_correcta}

    Proporciona una retroalimentación breve (máximo dos frases)
    con tono docente y constructivo.
    """

    try:
        if not client:
            raise ValueError("Falta configurar GEMINI_API_KEY")

        response = client.models.generate_content(
            model=modelo,
            contents=prompt
        )
        feedback = response.text.strip()
        logging.info("💬 Retroalimentación generada con éxito.")
        return feedback
    except Exception as e:
        logging.error(f"❌ Error al generar retroalimentación: {e}")
        return "No se pudo generar la retroalimentación."


# ─────────────────────────────────────────────────────────────
# 🧾 3. Calificar lista de respuestas automáticamente
# ─────────────────────────────────────────────────────────────
def calificar_respuestas_ia(intentos: List[Dict]) -> List[Dict]:
    """
    Evalúa respuestas del estudiante comparando texto exacto.
    Devuelve lista con es_correcta y retroalimentación generada por IA.
    """
    resultados = []
    for item in intentos:
        pregunta = item.get("pregunta", "")
        respuesta = item.get("respuesta", "")
        correcta = item.get("respuesta_correcta", "")

        es_correcta = respuesta.strip().lower() == correcta.strip().lower()
        feedback = generar_explicacion(pregunta, respuesta, correcta)

        resultados.append({
            "pregunta": pregunta,
            "respuesta": respuesta,
            "es_correcta": es_correcta,
            "retroalimentacion_ia": feedback
        })

    return resultados


# ─────────────────────────────────────────────────────────────
# ✅ 4. Prueba local
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tema = "Ciencias Naturales – Energía y Medio Ambiente"
    quiz = generar_quiz_automatico(tema, cantidad_preguntas=3)
    for i, q in enumerate(quiz, 1):
        print(f"\n{i}. {q['pregunta']}")
        for opcion in q["opciones"]:
            print(f"   - {opcion}")
        print(f"✅ Correcta: {q['respuesta_correcta']}")
        print(f"💡 Explicación: {q['explicacion']}")
