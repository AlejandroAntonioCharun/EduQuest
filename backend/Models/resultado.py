from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ResultadoAula(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    id_aula: str
    id_quiz: str
    promedio_puntaje: float
    fecha_generacion: datetime = datetime.utcnow()
    generado_por: str  # "sistema" | "IA"

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
