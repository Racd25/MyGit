import requests

def obtener_dolar_bcv():
    url = "https://pydolarve.org/api/v2/tipo-cambio"
    respuesta = requests.get(url)

    if respuesta.status_code == 200:
        datos = respuesta.json()
        precio_usd = datos.get("monitors", {}).get("usd", {}).get("price_old", None)

        if precio_usd is not None:
             return float(precio_usd)  # Asegúrate de devolverlo como número
        else:
             return float(1)
    else:
        print("Error al consultar la API.")
    
    return None  # Si falla, retorna None



def guardar_tasa_en_archivo(tasa, nombre_archivo="tasa.txt"):
    """
    Guarda el valor de la variable 'tasa' en un archivo de texto.
    
    Args:
        tasa (float or str): Valor a guardar.
        nombre_archivo (str): Nombre del archivo donde se guardará.
    """
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(str(tasa))
        print(f"Tasa guardada correctamente en '{nombre_archivo}'")
    except Exception as e:
        print(f"Error al guardar la tasa: {e}")
