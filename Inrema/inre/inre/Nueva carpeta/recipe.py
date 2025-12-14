import json
from pymongo import MongoClient

# --- Configuración ---
ARCHIVO_JSON = "BDmotores_tabla.json"
BASE_DE_DATOS = "Inrema"
COLECCION = "BDmotores"

# --- Conexión a MongoDB ---
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client[BASE_DE_DATOS]
    collection = db[COLECCION]
    print("✅ Conexión exitosa a MongoDB")
except Exception as e:
    print(f"❌ Error al conectar a MongoDB: {e}")
    exit(1)

# --- Cargar datos desde el archivo JSON ---
try:
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    print(f"✅ Datos cargados desde '{ARCHIVO_JSON}': {len(datos)} registros")
except FileNotFoundError:
    print(f"❌ No se encontró el archivo: {ARCHIVO_JSON}")
    exit(1)
except Exception as e:
    print(f"❌ Error al leer el archivo JSON: {e}")
    exit(1)

# --- Insertar en MongoDB ---
try:
    if datos:
        # Opción 1: Insertar muchos documentos
        result = collection.insert_many(datos)
        print(f"✅ Se insertaron {len(result.inserted_ids)} registros en '{COLECCION}'")

        # Opcional: Mostrar los primeros 3
        print("\n📌 Primeros 3 documentos insertados:")
        for doc in datos[:3]:
            print(doc)
    else:
        print("⚠️ No hay datos para insertar.")
except Exception as e:
    print(f"❌ Error al insertar en MongoDB: {e}")

# --- Cerrar conexión ---
client.close()
print("🔌 Conexión a MongoDB cerrada.")