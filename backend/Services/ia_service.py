# IA SERVICE – Generacion y retroalimentacion con Google Gemini
# Compatible con google-genai >= 1.0.0

import json
import logging
from typing import Dict, List

from decouple import config
from google import genai

# Configuracion del cliente de Gemini
GEMINI_API_KEY = config("GEMINI_API_KEY", default="")


def _build_client():
    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY no esta configurado; IA deshabilitada.")
        return None
    try:
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception as exc:
        logging.error(f"No se pudo inicializar el cliente de Gemini: {exc}")
        return None


client = _build_client()
logging.basicConfig(level=logging.INFO)


# 1. Generar preguntas de opcion multiple
def generar_quiz_automatico(
    tema: str,
    cantidad_preguntas: int = 5,
    modelo: str = "gemini-2.0-flash",
) -> List[Dict]:
    """
    Genera un cuestionario educativo de opcion multiple sobre un tema dado.
    Devuelve lista de preguntas u [] si no hay API key o falla la generacion.
    """
    prompt = f"""
    Crea un cuestionario educativo sobre el tema "{tema}".
    Debe contener exactamente {cantidad_preguntas} preguntas de opcion multiple.
    Devuelvelo como JSON valido con esta estructura exacta:
    [
      {{
        "pregunta": "texto de la pregunta",
        "opciones": ["opcion A", "opcion B", "opcion C", "opcion D"],
        "respuesta_correcta": "texto exacto de la respuesta correcta",
        "explicacion": "explicacion corta"
      }}
    ]
    No incluyas texto fuera del JSON.
    """

    if not client:
        return []

    try:
        response = client.models.generate_content(model=modelo, contents=prompt)
        content = (response.text or "").strip("`").strip()
        if not content.startswith("["):
            content = content[content.find("[") :]
        quiz_data = json.loads(content)
        logging.info("Se generaron %s preguntas sobre '%s'.", len(quiz_data), tema)
        return quiz_data
    except Exception as exc:
        logging.error("Error al generar el quiz: %s", exc)
        return []


# 2. Generar retroalimentacion personalizada
def generar_explicacion(
    pregunta: str,
    respuesta_usuario: str,
    respuesta_correcta: str,
    modelo: str = "gemini-2.0-flash",
) -> str:
    """
    Genera retroalimentacion educativa corta sobre una respuesta.
    """
    prompt = f"""
    Evalua esta pregunta:
    Pregunta: {pregunta}
    Respuesta del usuario: {respuesta_usuario}
    Respuesta correcta: {respuesta_correcta}

    Proporciona una retroalimentacion breve (maximo dos frases)
    con tono docente y constructivo.
    """

    if not client:
        return "Configura GEMINI_API_KEY para habilitar feedback con IA."

    try:
        response = client.models.generate_content(model=modelo, contents=prompt)
        feedback = (response.text or "").strip()
        logging.info("Retroalimentacion generada con exito.")
        return feedback
    except Exception as exc:
        logging.error("Error al generar retroalimentacion: %s", exc)
        return "No se pudo generar la retroalimentacion."


# 3. Calificar lista de respuestas automaticamente
def calificar_respuestas_ia(intentos: List[Dict]) -> List[Dict]:
    """
    Evalua respuestas del estudiante comparando texto exacto.
    Devuelve lista con es_correcta y retroalimentacion generada por IA.
    """
    resultados = []
    for item in intentos:
        pregunta = item.get("pregunta", "")
        respuesta = item.get("respuesta", "")
        correcta = item.get("respuesta_correcta", "")

        es_correcta = respuesta.strip().lower() == correcta.strip().lower()
        feedback = generar_explicacion(pregunta, respuesta, correcta)

        resultados.append(
            {
                "pregunta": pregunta,
                "respuesta": respuesta,
                "es_correcta": es_correcta,
                "retroalimentacion_ia": feedback,
            }
        )

    return resultados


# Prueba local
if __name__ == "__main__":
    tema = "Ciencias Naturales - Energia y Medio Ambiente"
    quiz = generar_quiz_automatico(tema, cantidad_preguntas=3)
    for i, q in enumerate(quiz, 1):
        print(f"\n{i}. {q['pregunta']}")
        for opcion in q["opciones"]:
            print(f"   - {opcion}")
        print(f"Correcta: {q['respuesta_correcta']}")
        print(f"Explicacion: {q['explicacion']}")
