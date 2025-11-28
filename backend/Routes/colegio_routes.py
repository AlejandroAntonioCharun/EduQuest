from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

from config import db

router = APIRouter()


class ColegioCreate(BaseModel):
    nombre: str
    direccion: str
    telefono: Optional[str] = None
    correo_institucional: Optional[str] = None


class ColegioUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo_institucional: Optional[str] = None


def serialize_colegio(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/")
async def listar_colegios():
    colegios = await db.colegios.find().to_list(200)
    return [serialize_colegio(c) for c in colegios]


@router.post("/")
async def crear_colegio(payload: ColegioCreate):
    data = payload.dict()
    result = await db.colegios.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return data


@router.put("/{colegio_id}")
async def actualizar_colegio(colegio_id: str, payload: ColegioUpdate):
    update_data = {k: v for k, v in payload.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    result = await db.colegios.update_one({"_id": ObjectId(colegio_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Colegio no encontrado")

    actualizado = await db.colegios.find_one({"_id": ObjectId(colegio_id)})
    return serialize_colegio(actualizado)
