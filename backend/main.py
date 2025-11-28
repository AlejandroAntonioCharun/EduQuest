# ============================================================
# 🧠 EDUQUEST API
# FastAPI + MongoDB Atlas + Gemini IA
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import db
from Routes import (
    user_routes,
    quiz_routes,
    intento_routes,
    ia_routes,
    docente_routes,
    estudiante_routes,
    colegio_routes,
)

# ------------------------------------------------------------
# 🚀 Inicialización de la aplicación
# ------------------------------------------------------------
app = FastAPI(
    title="EduQuest API",
    description="Plataforma educativa con IA (Gemini) para creación y evaluación de quizzes.",
    version="1.0.0",
    contact={
        "name": "Asfood / EduQuest Dev Team",
        "url": "https://eduquest.ai",
        "email": "alejandro.charun@eduquest.pe",
    },
)

# ------------------------------------------------------------
# 🌍 Configuración de CORS
# ------------------------------------------------------------
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://eduquest.vercel.app",
    "https://edu-quest-deploy.vercel.app",  # Dominio de producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# 🔗 Registro de Rutas
# ------------------------------------------------------------
app.include_router(user_routes.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(quiz_routes.router, prefix="/quiz", tags=["Quizzes"])
app.include_router(intento_routes.router, prefix="/intento", tags=["Intentos"])
app.include_router(ia_routes.router, prefix="/ia", tags=["Inteligencia Artificial"])
app.include_router(docente_routes.router, prefix="/docentes", tags=["Docentes"])
app.include_router(estudiante_routes.router, prefix="/estudiantes", tags=["Estudiantes"])
app.include_router(colegio_routes.router, prefix="/colegios", tags=["Colegios"])

# ------------------------------------------------------------
# 🏠 Ruta raíz
# ------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "🚀 API EduQuest corriendo correctamente",
        "status": "OK",
        "version": "1.0.0",
        "components": ["FastAPI", "MongoDB Atlas", "Gemini 1.5 Flash"],
    }

# ------------------------------------------------------------
# 🧪 Verificar conexión a MongoDB Atlas
# ------------------------------------------------------------
@app.get("/status/db")
async def check_db_connection():
    try:
        # Prueba simple: contar colecciones
        collections = await db.list_collection_names()
        return {
            "database": "MongoDB Atlas conectado",
            "collections": collections,
            "status": "OK"
        }
    except Exception as e:
        return {
            "database": "Error de conexión",
            "details": str(e),
            "status": "FAIL"
        }
