from pydantic import BaseModel, Field
from typing import Optional

class Aula(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    id_docente: str
    nombre_aula: str
    grado: str
    seccion: str
    año_academico: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
