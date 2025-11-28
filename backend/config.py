from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de MongoDB Atlas
MONGODB_URI = "mongodb+srv://admin_db_user:IEB4xLTkxLMb4MEc@quizmaster.pidhin3.mongodb.net/?appName=QuizMaster"
DB_NAME = "eduquest"

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

# API Key de Gemini (reemplaza con la tuya)
GEMINI_API_KEY = os.getenv("AIzaSyBVe_ueEE5tfqYlcgQSFRzKT7i9Qmx_PVQ")
