from bson import ObjectId
from config import db

# ✅ Convertir ObjectId a string (útil para respuestas JSON)
def serialize_doc(doc):
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    return doc


# 🔹 Crear documento genérico
async def crear_documento(nombre_coleccion: str, data: dict):
    result = await db[nombre_coleccion].insert_one(data)
    data["_id"] = str(result.inserted_id)
    return data


# 🔹 Buscar documento por ID
async def obtener_por_id(nombre_coleccion: str, id: str):
    doc = await db[nombre_coleccion].find_one({"_id": ObjectId(id)})
    return serialize_doc(doc)


# 🔹 Listar documentos
async def listar_documentos(nombre_coleccion: str, filtro: dict = {}, limite: int = 100):
    docs = await db[nombre_coleccion].find(filtro).to_list(limite)
    return [serialize_doc(d) for d in docs]


# 🔹 Actualizar documento
async def actualizar_documento(nombre_coleccion: str, id: str, data: dict):
    result = await db[nombre_coleccion].update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )
    if result.matched_count == 0:
        return None
    return await obtener_por_id(nombre_coleccion, id)


# 🔹 Eliminar documento
async def eliminar_documento(nombre_coleccion: str, id: str):
    result = await db[nombre_coleccion].delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0


# 🔹 Simular populate usando $lookup (relaciones)
async def lookup(base: str, local_field: str, foreign_field: str, from_collection: str, filtro: dict = {}):
    pipeline = [
        {"$match": filtro},
        {"$lookup": {
            "from": from_collection,
            "localField": local_field,
            "foreignField": foreign_field,
            "as": f"{from_collection}_info"
        }},
        {"$unwind": {"path": f"${from_collection}_info", "preserveNullAndEmptyArrays": True}}
    ]
    result = await db[base].aggregate(pipeline).to_list(1)
    return serialize_doc(result[0]) if result else None
