from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Colegio(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    nombre: str
    direccion: str
    telefono: str
    email: str
    fecha_registro: datetime = datetime.utcnow()
    licencia_activa: bool = True

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
