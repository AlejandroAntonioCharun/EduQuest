import os
import sys

from mangum import Mangum

# Asegura que el módulo backend esté en el path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.append(BACKEND_DIR)

# Importa la app de FastAPI ya configurada
from main import app as fastapi_app  # type: ignore  # noqa: E402

# Exponer el handler compatible con Vercel (lambda-style)
handler = Mangum(fastapi_app)

# También exponemos app por si se quiere ejecutar directamente en otros entornos
app = fastapi_app
