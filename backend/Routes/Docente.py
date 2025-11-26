from fastapi import APIRouter, HTTPException
from db.connection import docentes_collection
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter(prefix="/docentes", tags=["Docentes"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Docente(BaseModel):
    nombre: str
    contraseña: str
    especialidad: str
    colegio: str
    cantidadAlumnos: int
    grado: str
    seccion: str
    etapa: str


@router.post("/register")
async def registrar_docente(docente: Docente):
    # Verificar si ya existe
    existente = await docentes_collection.find_one({"nombre": docente.nombre})
    if existente:
        raise HTTPException(status_code=400, detail="❌ El docente ya está registrado.")

    # Encriptar contraseña
    docente_dict = docente.dict()
    docente_dict["contraseña"] = pwd_context.hash(docente.contraseña)

    result = await docentes_collection.insert_one(docente_dict)
    docente_dict["_id"] = str(result.inserted_id)

    return {"message": "✅ Docente registrado correctamente", "docente": docente_dict}

# 🔵 Login de docente
@router.post("/login")
async def login_docente(data: dict):
    nombre = data.get("nombre")
    contraseña = data.get("contraseña")

    docente = await docentes_collection.find_one({"nombre": nombre})
    if not docente:
        raise HTTPException(status_code=404, detail="❌ Usuario no encontrado")

    if not pwd_context.verify(contraseña, docente["contraseña"]):
        raise HTTPException(status_code=401, detail="⚠️ Contraseña incorrecta")

    docente["_id"] = str(docente["_id"])
    return {"message": "✅ Inicio de sesión exitoso", "docente": docente}
