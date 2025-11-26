from fastapi import APIRouter, HTTPException
from db.connection import quiz_collection
from Models.preguntas_modelo import Quiz, Resultado
import random

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

# 🎯 Generar código PIN
def generar_pin():
    prefijo = random.choice(["AS", "CS", "HS", "QS", "MS"])
    numero = random.randint(1000, 9999)
    return f"{prefijo}-{numero}"

# 🎯 Generar preguntas simuladas (a reemplazar con Gemini luego)
def generar_preguntas_automaticas(nombre_quiz: str, cantidad: int = 5):
    preguntas = []
    for i in range(1, cantidad + 1):
        preguntas.append({
            "id": i,
            "pregunta": f"Pregunta {i} generada para {nombre_quiz}",
            "enunciado": "Selecciona la respuesta correcta.",
            "respuestaCorrecta": f"Respuesta {i}",
            "tiempo": 60,
            "puntaje": 10
        })
    return preguntas

# 🧩 Crear quiz
@router.post("/")
async def crear_quiz(quiz: Quiz):
    quiz.pin = generar_pin()
    quiz_dict = quiz.dict(exclude_unset=True)
    quiz_dict["lista_preguntas"] = generar_preguntas_automaticas(quiz.nombre, quiz.preguntas)
    quiz_dict["resultados"] = []
    result = await quiz_collection.insert_one(quiz_dict)
    quiz_dict["_id"] = str(result.inserted_id)
    return {
        "message": "✅ Quiz creado con éxito",
        "pin": quiz.pin,
        "quiz": quiz_dict
    }

# 📘 Obtener todos los quizzes
@router.get("/")
async def obtener_quizzes():
    quizzes = []
    async for q in quiz_collection.find():
        q["_id"] = str(q["_id"])
        quizzes.append(q)
    return quizzes

# 📗 Obtener un quiz por PIN
@router.get("/{pin}")
async def obtener_quiz_por_pin(pin: str):
    quiz = await quiz_collection.find_one({"pin": pin})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")
    quiz["_id"] = str(quiz["_id"])
    return quiz

# 🧠 Registrar resultado de un estudiante
@router.post("/{pin}/resultado")
async def registrar_resultado(pin: str, resultado: Resultado):
    quiz = await quiz_collection.find_one({"pin": pin})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")

    nuevo_resultado = resultado.dict()
    quiz["resultados"].append(nuevo_resultado)

    await quiz_collection.update_one(
        {"pin": pin},
        {"$set": {"resultados": quiz["resultados"]}}
    )
    return {"message": "Resultado agregado correctamente", "pin": pin}
