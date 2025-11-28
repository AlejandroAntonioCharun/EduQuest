from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from passlib.hash import bcrypt

from config import db

router = APIRouter()


class DocenteCreate(BaseModel):
    nombres: str
    apellidos: str
    dni: str
    password: str
    especialidad: Optional[str] = None
    id_colegio: Optional[str] = None
    colegio: Optional[str] = None
    cantidadAlumnos: Optional[int] = None
    grado: Optional[str] = None
    seccion: Optional[str] = None
    etapa: Optional[str] = None


class DocenteUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    dni: Optional[str] = None
    password: Optional[str] = None
    especialidad: Optional[str] = None
    id_colegio: Optional[str] = None
    colegio: Optional[str] = None
    cantidadAlumnos: Optional[int] = None
    grado: Optional[str] = None
    seccion: Optional[str] = None
    etapa: Optional[str] = None


def serialize_docente(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/")
async def listar_docentes():
    docentes = await db.docentes.find().to_list(200)
    return [serialize_docente(d) for d in docentes]


@router.post("/register")
async def registrar_docente(payload: DocenteCreate):
    existente = await db.docentes.find_one({"dni": payload.dni})
    if existente:
        raise HTTPException(status_code=400, detail="El docente ya existe")

    data = payload.dict()
    data["password"] = bcrypt.hash(payload.password)

    result = await db.docentes.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return data


@router.put("/{docente_id}")
async def actualizar_docente(docente_id: str, payload: DocenteUpdate):
    update_data = {k: v for k, v in payload.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    if "password" in update_data:
        update_data["password"] = bcrypt.hash(update_data["password"])

    result = await db.docentes.update_one({"_id": ObjectId(docente_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Docente no encontrado")

    actualizado = await db.docentes.find_one({"_id": ObjectId(docente_id)})
    return serialize_docente(actualizado)


@router.delete("/{docente_id}")
async def eliminar_docente(docente_id: str):
    result = await db.docentes.delete_one({"_id": ObjectId(docente_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    return {"mensaje": "Docente eliminado correctamente"}
