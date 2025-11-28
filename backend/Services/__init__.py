# ─────────────────────────────────────────────────────────────
# 📦 SERVICES PACKAGE INITIALIZER
# Centraliza las importaciones principales de los servicios.
# ─────────────────────────────────────────────────────────────

# IA – Generación y retroalimentación con Google Gemini
from .ia_service import (
    generar_quiz_automatico,
    generar_explicacion,
    calificar_respuestas_ia
)

# Si más adelante tienes otros módulos, puedes importarlos aquí:
# from .user_service import *
# from .quiz_service import *
# from .database_service import *
# etc.

# Para control explícito (evita conflictos y autoimports indeseados)
__all__ = [
    "generar_quiz_automatico",
    "generar_explicacion",
    "calificar_respuestas_ia",
]
