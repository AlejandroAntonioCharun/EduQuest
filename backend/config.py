from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGODB_URI = config("MONGODB_URI", default="")
client = AsyncIOMotorClient(MONGODB_URI)
db = client["eduquest"]
