from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Opcion(BaseModel):
    texto_opcion: str
    es_correcta: bool

class Pregunta(BaseModel):
    enunciado: str
    tipo: str  # "opcion_multiple" | "abierta"
    opciones: Optional[List[Opcion]] = None
    respuesta_correcta: Optional[str] = None
    generada_por_IA: bool = False

class Quiz(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    id_docente: str
    id_aula: str
    titulo: str
    descripcion: str
    fecha_creacion: datetime = datetime.utcnow()
    pin_acceso: str
    generado_por_IA: bool = False
    preguntas: List[Pregunta] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
