from fastapi import APIRouter, HTTPException
from Services.ia_service import (
    generar_quiz_automatico,
    generar_explicacion,
    calificar_respuestas_ia
)

import json

router = APIRouter(prefix="/ia", tags=["IA"])

# 🧩 Generar preguntas automáticas
@router.get("/preguntas")
async def generar_preguntas(tema: str, cantidad: int = 5):
    """
    Genera preguntas de opción múltiple usando Gemini.
    """
    try:
        preguntas_raw = generar_quiz_automatico(tema, cantidad_preguntas=cantidad)
        if isinstance(preguntas_raw, str):
            raise ValueError(preguntas_raw)

        return {
            "tema": tema,
            "cantidad": len(preguntas_raw),
            "preguntas_generadas": preguntas_raw
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error: Gemini devolvió un JSON inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando preguntas: {str(e)}")


# 💬 Generar retroalimentación simple
@router.get("/retroalimentacion")
async def generar_feedback(
    pregunta: str,
    respuesta_usuario: str,
    respuesta_correcta: str
):
    """
    Genera retroalimentación educativa breve con Gemini.
    """
    try:
        feedback = generar_explicacion(pregunta, respuesta_usuario, respuesta_correcta)
        return {
            "pregunta": pregunta,
            "respuesta_usuario": respuesta_usuario,
            "respuesta_correcta": respuesta_correcta,
            "retroalimentacion": feedback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando feedback: {str(e)}")


# 🧾 Calificar respuestas con IA
@router.post("/calificar")
async def calificar_respuestas(intentos: list):
    """
    Califica una lista de respuestas y genera retroalimentación IA.
    """
    try:
        resultados = calificar_respuestas_ia(intentos)
        return {"resultados": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calificar respuestas: {str(e)}")
