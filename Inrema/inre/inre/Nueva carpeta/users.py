from pymongo import MongoClient

# Conexión a MongoDB (por defecto en localhost:27017)
client = MongoClient('mongodb://localhost:27017/')

# Seleccionar la base de datos "Inrema"
db = client['Inrema']

# Seleccionar la colección "users" (se creará si no existe)
collection = db['users']

# Documento a insertar
usuario = {
    "usuario": "RACD",
    "contrasena": "123"
}

# Verificar si ya existe un usuario con "RACD" para evitar duplicados
existing_user = collection.find_one({"usuario": "RACD"})

if existing_user:
    print("El usuario 'RACD' ya existe en la base de datos.")
else:
    # Insertar el documento
    result = collection.insert_one(usuario)
    print(f"Usuario 'RACD' agregado con ID: {result.inserted_id}")

# Cerrar la conexión
client.close()