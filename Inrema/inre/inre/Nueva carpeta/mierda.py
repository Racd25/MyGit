from pymongo import MongoClient


def corregir_contador_repuestos():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Inrema']
    repuestos = db['Repuestos']
    counters = db['counters']

    # Obtener el máximo código actual
    pipeline = [{"$group": {"_id": None, "max_codigo": {"$max": "$codigo"}}}]
    resultado = list(repuestos.aggregate(pipeline))
    max_codigo = resultado[0]['max_codigo'] if resultado and resultado[0]['max_codigo'] is not None else 0

    # Establecer el contador en max_codigo + 1
    nuevo_valor = max_codigo + 1
    counters.update_one(
        {"_id": "repuestos_codigo"},
        {"$set": {"seq": nuevo_valor}},
        upsert=True  # Crea el documento si no existe
    )

    print(f"✅ Contador actualizado a: {nuevo_valor}")
    client.close()

if __name__ == "__main__":
    corregir_contador_repuestos()