import json
from pymongo import MongoClient

# === CONFIGURACIÓN ===
MONGO_URI = 'mongodb://localhost:27017/'
NOMBRE_BASE_DE_DATOS = 'Inrema'
NOMBRE_COLECCION = 'BDmotores'
ARCHIVO_JSON = 'output.json'  # Asegúrate de que esté en la misma carpeta

def cargar_json_a_mongodb():
    try:
        # 1. Leer el archivo JSON
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as file:
            datos = json.load(file)

        if not isinstance(datos, list):
            print(f"❌ Error: El archivo {ARCHIVO_JSON} no es una lista.")
            return

        print(f"✅ Se cargaron {len(datos)} registros desde {ARCHIVO_JSON}")

        # 2. Conectar a MongoDB
        client = MongoClient(MONGO_URI)
        db = client[NOMBRE_BASE_DE_DATOS]
        collection = db[NOMBRE_COLECCION]

        # Opcional: eliminar todos los documentos antes de insertar (para evitar duplicados)
        # collection.delete_many({})

        # 3. Insertar todos los documentos
        if datos:
            result = collection.insert_many(datos, ordered=False)  # Ignora errores individuales
            print(f"🚀 Insertados {len(result.inserted_ids)} documentos en '{NOMBRE_COLECCION}'")
        else:
            print("⚠️ No hay datos para insertar.")

        client.close()

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {ARCHIVO_JSON}")
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer el archivo JSON: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

# === Ejecutar función ===
if __name__ == "__main__":
    cargar_json_a_mongodb()