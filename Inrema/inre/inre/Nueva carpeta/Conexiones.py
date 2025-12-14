from pymongo import MongoClient
from pymongo import MongoClient

# Conexión local
local_client = MongoClient("mongodb://localhost:27017")
local_db = local_client["Marron"]
local_collection = local_db["Inrema"]

# Conexión Atlas
atlas_client = MongoClient("mongodb+srv://<usuario>:<contraseña>@cluster0.oylpxf6.mongodb.net")
atlas_db = atlas_client["Morada"]
atlas_collection = atlas_db["Inrema"]

# Transferencia de datos
docs = list(local_collection.find())
if docs:
    atlas_collection.insert_many(docs)