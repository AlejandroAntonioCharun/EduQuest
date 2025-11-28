from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Estudiante(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    id_usuario: str
    id_aula: Optional[str] = None
    nombres: str
    apellidos: str
    dni: str
    fecha_registro: datetime = datetime.utcnow()

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
