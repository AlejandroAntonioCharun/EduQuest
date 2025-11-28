from fastapi import APIRouter, HTTPException
from config import db
from Models.usuario import Usuario
from bson import ObjectId
from passlib.hash import bcrypt

router = APIRouter()

# 🧩 Crear un nuevo usuario (docente o estudiante)
@router.post("/")
async def crear_usuario(usuario: Usuario):
    # Validar si ya existe
    existente = await db.usuarios.find_one({"email": usuario.email})
    if existente:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    usuario.password = bcrypt.hash(usuario.password)
    nuevo = usuario.dict(by_alias=True)
    result = await db.usuarios.insert_one(nuevo)
    nuevo["_id"] = str(result.inserted_id)
    return nuevo


# 🔎 Obtener usuario por ID
@router.get("/{usuario_id}")
async def obtener_usuario(usuario_id: str):
    usuario = await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario["_id"] = str(usuario["_id"])
    return usuario


# 📋 Listar todos los usuarios (solo admin)
@router.get("/")
async def listar_usuarios():
    usuarios = await db.usuarios.find().to_list(100)
    for u in usuarios:
        u["_id"] = str(u["_id"])
    return usuarios
