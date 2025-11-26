from pydantic import BaseModel, Field
from typing import List, Optional

# 🔹 Modelo de cada pregunta
class Pregunta(BaseModel):
    id: int
    pregunta: str
    enunciado: str
    respuestaCorrecta: str
    tiempo: int = Field(default=60)
    puntaje: int = Field(default=10)

# 🔹 Detalle de cada pregunta respondida por un estudiante
class DetalleResultado(BaseModel):
    pregunta: str
    respuesta: str
    resultado: str  # "Correcta" o "Incorrecta"

# 🔹 Resultado completo del estudiante
class Resultado(BaseModel):
    estudiante: str
    nota_total: int
    correctas: int
    incorrectas: int
    detalle: List[DetalleResultado]

# 🔹 Modelo principal del quiz
class Quiz(BaseModel):
    nombre: str
    clase: str
    formato: str
    dificultad: str
    preguntas: int = Field(default=5, description="Número de preguntas a generar")
    pin: Optional[str] = None
    lista_preguntas: Optional[List[Pregunta]] = []
    resultados: Optional[List[Resultado]] = []
