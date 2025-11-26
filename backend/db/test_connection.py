
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://admin_db_user:IEB4xLTkxLMb4MEc@quizmaster.pidhin3.mongodb.net/?appName=QuizMaster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Desarrollo correcto. se ha tenido coneccion con MongoDB!")
except Exception as e:
    print(e)