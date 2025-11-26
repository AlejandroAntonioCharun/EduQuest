from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes import Preguntas, Resultados, Docente

app = FastAPI(title="QuizMaster API", version="1.0")

# Permitir acceso desde tu frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar por tu dominio en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(Preguntas.router)
app.include_router(Resultados.router)
app.include_router(Docente.router)

@app.get("/")
async def root():
    return {"message": "API QuizMaster activa"}
