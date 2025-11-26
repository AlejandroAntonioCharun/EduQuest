from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

# URL de conexión a MongoDB Atlas o local
MONGO_URI = config("MONGO_URI", default="mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URI)
database = client["quizmaster"]

# Colecciones
quiz_collection = database.get_collection("quizzes")
result_collection = database.get_collection("results")
docentes_collection = database["docentes"]