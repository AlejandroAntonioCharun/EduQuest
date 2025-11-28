from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from passlib.hash import bcrypt

from config import db

router = APIRouter()


class EstudianteCreate(BaseModel):
    dni: str
    nombre: str
    apellidos: str
    password: str
    id_colegio: Optional[str] = None
    colegio: Optional[str] = None
    grado: Optional[str] = None
    seccion: Optional[str] = None
    etapa: Optional[str] = None
    id_clase: Optional[str] = None


class EstudianteUpdate(BaseModel):
    dni: Optional[str] = None
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    password: Optional[str] = None
    id_colegio: Optional[str] = None
    colegio: Optional[str] = None
    grado: Optional[str] = None
    seccion: Optional[str] = None
    etapa: Optional[str] = None
    id_clase: Optional[str] = None


def serialize_estudiante(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/")
async def listar_estudiantes():
    estudiantes = await db.estudiantes.find().to_list(200)
    return [serialize_estudiante(e) for e in estudiantes]


@router.post("/register")
async def crear_estudiante(payload: EstudianteCreate):
    existente = await db.estudiantes.find_one({"dni": payload.dni})
    if existente:
        raise HTTPException(status_code=400, detail="El estudiante ya existe")

    data = payload.dict()
    data["nombres"] = payload.nombre
    data["password"] = bcrypt.hash(payload.password)

    result = await db.estudiantes.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return data


@router.put("/{estudiante_id}")
async def actualizar_estudiante(estudiante_id: str, payload: EstudianteUpdate):
    update_data = {k: v for k, v in payload.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    if "password" in update_data:
        update_data["password"] = bcrypt.hash(update_data["password"])
    if "nombre" in update_data:
        update_data["nombres"] = update_data["nombre"]

    result = await db.estudiantes.update_one({"_id": ObjectId(estudiante_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    actualizado = await db.estudiantes.find_one({"_id": ObjectId(estudiante_id)})
    return serialize_estudiante(actualizado)


@router.delete("/{estudiante_id}")
async def eliminar_estudiante(estudiante_id: str):
    result = await db.estudiantes.delete_one({"_id": ObjectId(estudiante_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return {"mensaje": "Estudiante eliminado correctamente"}
