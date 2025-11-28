import random
import string
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from config import db
from Services.ia_service import generar_quiz_automatico

router = APIRouter()


class RespuestaPayload(BaseModel):
    id_pregunta: str
    opcion: str


class EnvioQuizPayload(BaseModel):
    dni: Optional[str] = None
    id_estudiante: Optional[str] = None
    respuestas: List[RespuestaPayload]


class QuizUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None


def _serialize_quiz(quiz: dict) -> dict:
    quiz["_id"] = str(quiz["_id"])
    preguntas = []
    for p in quiz.get("preguntas", []):
        if isinstance(p.get("_id"), ObjectId):
            p["_id"] = str(p["_id"])
        preguntas.append(p)
    quiz["preguntas"] = preguntas
    return quiz


def _pin() -> str:
    return "".join(random.choices(string.digits, k=6))


def _detalle_respuesta(pregunta: dict, seleccion: str) -> dict:
    correcta = ""
    for op in pregunta.get("opciones", []):
        if op.get("es_correcta"):
            correcta = op.get("texto_opcion", "")
            break
    return {
        "pregunta_id": str(pregunta.get("_id")),
        "pregunta": pregunta.get("texto_pregunta", "Pregunta"),
        "opcion_seleccionada": seleccion,
        "respuesta_correcta": correcta,
        "correcta": seleccion == correcta if correcta else False,
        "puntaje_obtenido": 1 if correcta and seleccion == correcta else 0,
    }


@router.get("/")
async def listar_quizzes():
    quizzes = await db.quizzes.find().to_list(200)
    return [_serialize_quiz(q) for q in quizzes]


@router.get("/pin/{pin}")
async def obtener_quiz_por_pin(pin: str):
    quiz = await db.quizzes.find_one({"pin_acceso": pin})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")
    return _serialize_quiz(quiz)


@router.get("/{pin}/feedback")
async def obtener_feedback(
    pin: str,
    dni: Optional[str] = None,
    estudiante_id: Optional[str] = Query(default=None, alias="estudiante_id"),
):
    if not dni and not estudiante_id:
        raise HTTPException(status_code=400, detail="Debes enviar dni o estudiante_id")

    query = {"pin_acceso": pin}
    if dni:
        query["dni"] = dni
    if estudiante_id:
        query["id_estudiante"] = estudiante_id

    intento = await db.intentos_quiz.find_one(query, sort=[("creado_en", -1)])
    if not intento:
        return {"has_feedback": False}

    quiz = await db.quizzes.find_one({"pin_acceso": pin}) or {}
    preguntas = {str(p.get("_id")): p for p in quiz.get("preguntas", [])}

    detalle = []
    for r in intento.get("detalle", []):
        pregunta_doc = preguntas.get(r.get("pregunta_id"))
        detalle.append(
            {
                "pregunta_id": r.get("pregunta_id"),
                "pregunta": r.get("pregunta") or (pregunta_doc or {}).get("texto_pregunta", "Pregunta"),
                "opcion_seleccionada": r.get("opcion_seleccionada", ""),
                "respuesta_correcta": r.get("respuesta_correcta", ""),
                "correcta": r.get("correcta", False),
                "puntaje_obtenido": r.get("puntaje_obtenido", 0),
                "feedback": r.get("feedback", ""),
            }
        )

    return {
        "has_feedback": True,
        "detalle": detalle,
        "puntaje_total": intento.get("puntaje_total", 0),
    }


@router.post("/{pin}/responder")
async def responder_quiz(pin: str, payload: EnvioQuizPayload):
    quiz = await db.quizzes.find_one({"pin_acceso": pin})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")

    preguntas = {str(p.get("_id")): p for p in quiz.get("preguntas", [])}
    detalle = []
    correctas = 0

    for resp in payload.respuestas:
        pregunta = preguntas.get(resp.id_pregunta)
        if not pregunta:
            continue
        detalle_item = _detalle_respuesta(pregunta, resp.opcion)
        if detalle_item["correcta"]:
            correctas += 1
        detalle.append(detalle_item)

    puntaje_total = correctas

    intento = {
        "pin_acceso": pin,
        "quiz_id": str(quiz.get("_id")),
        "dni": payload.dni,
        "id_estudiante": payload.id_estudiante,
        "detalle": detalle,
        "puntaje_total": puntaje_total,
        "creado_en": datetime.utcnow(),
    }
    await db.intentos_quiz.insert_one(intento)

    return {
        "mensaje": "Respuestas registradas",
        "detalle": detalle,
        "puntaje_total": puntaje_total,
    }


@router.post("/ia/generar")
async def generar_quiz_ia(
    tema: str,
    curso: str,
    grado: str,
    numero_preguntas: int = 5,
    id_docente: Optional[str] = None,
    id_tema: Optional[str] = None,
):
    try:
        preguntas_raw = generar_quiz_automatico(tema, cantidad_preguntas=numero_preguntas)
    except Exception:
        preguntas_raw = []

    if not preguntas_raw:
        preguntas_raw = [
            {
                "pregunta": f"Pregunta sobre {tema} #{i+1}",
                "opciones": ["Opcion A", "Opcion B", "Opcion C", "Opcion D"],
                "respuesta_correcta": "Opcion A",
                "explicacion": "Respuesta generada por defecto",
            }
            for i in range(numero_preguntas)
        ]

    preguntas = []
    for q in preguntas_raw:
        correcta = q.get("respuesta_correcta", "")
        preguntas.append(
            {
                "_id": str(ObjectId()),
                "texto_pregunta": q.get("pregunta", "Pregunta"),
                "descripcion": q.get("explicacion", ""),
                "opciones": [
                    {"texto_opcion": op, "es_correcta": op == correcta}
                    for op in q.get("opciones", [])
                ],
            }
        )

    quiz_doc = {
        "titulo": f"{tema} - {curso}".strip(" -"),
        "descripcion": f"Quiz autogenerado para {grado}" if grado else "Quiz autogenerado",
        "pin_acceso": _pin(),
        "preguntas": preguntas,
        "id_docente": id_docente,
        "id_tema": id_tema,
        "generado_por_IA": True,
        "fecha_creacion": datetime.utcnow(),
    }

    result = await db.quizzes.insert_one(quiz_doc)
    quiz_doc["_id"] = str(result.inserted_id)
    return quiz_doc


@router.put("/{quiz_id}")
async def actualizar_quiz(quiz_id: str, payload: QuizUpdate):
    update_data = {k: v for k, v in payload.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    result = await db.quizzes.update_one({"_id": ObjectId(quiz_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")

    quiz = await db.quizzes.find_one({"_id": ObjectId(quiz_id)})
    return _serialize_quiz(quiz)


@router.delete("/{quiz_id}")
async def eliminar_quiz(quiz_id: str):
    result = await db.quizzes.delete_one({"_id": ObjectId(quiz_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")

    await db.intentos_quiz.delete_many({"quiz_id": quiz_id})
    return {"mensaje": "Quiz eliminado correctamente"}
