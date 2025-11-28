from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from datetime import datetime

class Usuario(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    password: str
    rol: Literal["docente", "estudiante", "admin"]
    activo: bool = True
    fecha_creacion: datetime = datetime.utcnow()
    ultimo_login: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
