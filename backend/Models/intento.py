from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RespuestaEstudiante(BaseModel):
    id_pregunta: str
    respuesta: str
    es_correcta: bool = False
    retroalimentacion_ia: Optional[str] = ""

class IntentoQuiz(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    id_estudiante: str
    id_quiz: str
    fecha_inicio: datetime = datetime.utcnow()
    fecha_envio: Optional[datetime] = None
    puntaje_total: float = 0
    evaluado_por_IA: bool = False
    respuestas: List[RespuestaEstudiante]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
