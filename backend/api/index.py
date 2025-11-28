from fastapi import FastAPI
from mangum import Mangum
from main import app  # Importamos la app principal

# Handler para Vercel
handler = Mangum(app)
