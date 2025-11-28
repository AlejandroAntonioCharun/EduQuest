from fastapi import APIRouter, HTTPException
from config import db
from Models.intento import IntentoQuiz
from bson import ObjectId
from Services.ia_service import calificar_respuestas_ia

router = APIRouter()


# ✍️ Registrar intento
@router.post("/")
async def registrar_intento(intento: IntentoQuiz):
    intento_dict = intento.dict(by_alias=True)
    result = await db.intentos_quiz.insert_one(intento_dict)
    intento_dict["_id"] = str(result.inserted_id)
    return intento_dict


# 🧠 Nuevo: Evaluar intento con IA (Gemini)
@router.post("/{intento_id}/evaluar-ia")
async def evaluar_intento_con_ia(intento_id: str):
    """
    Evalúa un intento de quiz usando IA: 
    - Verifica respuestas correctas
    - Genera retroalimentación por pregunta
    - Calcula el puntaje total
    """
    intento = await db.intentos_quiz.find_one({"_id": ObjectId(intento_id)})
    if not intento:
        raise HTTPException(status_code=404, detail="Intento no encontrado")

    # Generar evaluación con IA
    respuestas_con_feedback = await calificar_respuestas_ia(intento["respuestas"])

    correctas = sum(1 for r in respuestas_con_feedback if r["es_correcta"])
    puntaje = (correctas / len(respuestas_con_feedback)) * 20

    # Actualizar intento en BD
    await db.intentos_quiz.update_one(
        {"_id": ObjectId(intento_id)},
        {"$set": {
            "respuestas": respuestas_con_feedback,
            "puntaje_total": puntaje,
            "evaluado_por_IA": True
        }}
    )

    intento["respuestas"] = respuestas_con_feedback
    intento["puntaje_total"] = puntaje
    intento["evaluado_por_IA"] = True

    return {
        "mensaje": "✅ Intento evaluado por IA exitosamente",
        "puntaje_total": puntaje,
        "respuestas": respuestas_con_feedback
    }
