from fastapi import APIRouter, HTTPException
from db.connection import result_collection
from Models.preguntas_modelo import Resultado

router = APIRouter(prefix="/results", tags=["Resultados"])

@router.post("/{pin}")
async def registrar_resultado(pin: str, resultado: Resultado):
    res_dict = resultado.dict()
    res_dict["pin"] = pin
    result = await result_collection.insert_one(res_dict)
    return {"message": "Resultado guardado", "id": str(result.inserted_id)}

@router.get("/{pin}")
async def obtener_resultados(pin: str):
    resultados = []
    async for r in result_collection.find({"pin": pin}):
        r["_id"] = str(r["_id"])
        resultados.append(r)
    if not resultados:
        raise HTTPException(status_code=404, detail="No hay resultados para este quiz")
    return resultados
