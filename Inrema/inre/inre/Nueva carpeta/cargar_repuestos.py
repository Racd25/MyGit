import json
from pymongo import MongoClient

def cargar_repuestos_a_mongo(json_file='repuestos.json', db_name='Inrema', collection_name='Repuestos'):
    try:
        # 1. Leer el archivo JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            repuestos = json.load(f)

        # Validar que sea una lista
        if not isinstance(repuestos, list):
            raise ValueError("El archivo JSON debe contener un array de repuestos.")

        # 2. Añadir campo 'codigo' secuencial (1, 2, 3, ...)
        for i, repuesto in enumerate(repuestos, start=1):
            repuesto['codigo'] = i  # Sobrescribe si ya existe, o lo crea

        # 3. Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db[collection_name]

        # 4. Limpiar la colección (opcional: descomenta si quieres reemplazar todos los datos)
        # collection.delete_many({})

        # 5. Insertar los repuestos
        if repuestos:
            result = collection.insert_many(repuestos)
            print(f"✅ Insertados {len(result.inserted_ids)} repuestos en la colección '{collection_name}'.")
            print(f"   Los códigos asignados van del 1 al {len(repuestos)}.")
        else:
            print("⚠️ El archivo JSON está vacío. No se insertó nada.")

        # 6. Cerrar conexión
        client.close()

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{json_file}'.")
    except json.JSONDecodeError as e:
        print(f"❌ Error: El archivo no es un JSON válido. Detalles: {e}")
    except Exception as e:
        print(f"❌ Error al conectar con MongoDB o insertar datos: {e}")

# Ejecutar la función
if __name__ == "__main__":
    cargar_repuestos_a_mongo()