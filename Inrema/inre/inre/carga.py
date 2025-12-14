from pathlib import Path
from sqlqueries import QueriesSQLite  # ← Cambia "your_module" por el nombre del archivo donde está QueriesSQLite

# Ruta a la base de datos
import sqlite3

# Conexión a la base de datos (reemplaza 'mi_base_de_datos.db' con el nombre real)
conn = sqlite3.connect('pdvDB.sqlite')
cursor = conn.cursor()

# Nombres de las tablas que quieres eliminar
tablas_a_borrar = ['recipes']

try:
    for tabla in tablas_a_borrar:
        cursor.execute(f"DROP TABLE IF EXISTS {tabla}")
        print(f"Tabla '{tabla}' eliminada con éxito.")
    conn.commit()
except Exception as e:
    print(f"Error al borrar las tablas: {e}")
finally:
    conn.close()

    
def insertar_consulta(connection, consulta_tuple):
    """
    Inserta una nueva consulta en la tabla 'consultas' usando una tupla.
    
    Args:
        connection: Conexión activa a la base de datos SQLite.
        consulta_tuple (tuple): Tupla con los valores a insertar, en el orden correcto.
                               Debe tener 18 valores (uno por cada campo excepto 'id' y 'fecha_registro').
    """
    insert_query = """
    INSERT INTO consultas (
        nombre_propietario, ci, telefono, direccion, motivo_consulta,
        nombre_mascota, especie, raza, sexo, edad, pelaje, cc,
        despa2, vacuna, alimentacion, enfermedad, tratamiento, anamnesis
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        QueriesSQLite.execute_query(connection, insert_query, consulta_tuple)
        print("✅ Consulta guardada exitosamente.")
        return True
    except Exception as e:
        print(f"❌ Error al guardar consulta: {e}")
        return False
    
# Datos de ejemplo (deben estar en el mismo orden que en la consulta SQL)
consulta_data = (
    "María Pérez",           # nombre_propietario
    "12345678",              # ci
    "0412-1234567",          # telefono
    "Calle Principal #123",  # direccion
    "Consulta de rutina",     # motivo_consulta
    "Firulais",              # nombre_mascota
    "Perro",                 # especie
    "Pastor Alemán",         # raza
    "Macho",                 # sexo
    5.5,                     # edad (REAL)
    "Pelo corto negro",      # pelaje
    "CC123",                 # cc
    "Sí, última semana",     # despa2
    "Vacuna antirrábica",    # vacuna
    "Croquetas premium",     # alimentacion
    "Ninguna",               # enfermedad
    "Ninguno",               # tratamiento
    "Mascota activa, buen apetito."  # anamnesis
)
def imprimir_todas_las_consultas():
    """
    Conecta a la base de datos y muestra todos los registros de la tabla 'consultas'.
    """
    connection = QueriesSQLite.create_connection("pdvDB.sqlite")
    
    select_query = """
    SELECT * FROM examen_laboratorio
    """
    
    try:
        consultas = QueriesSQLite.execute_read_query(connection, select_query)
        
        if consultas:
            print(f"\n{'='*80}")
            print("📋 TODOS LOS REGISTROS DE CONSULTAS")
            print(f"{'='*80}")
            for consulta in consultas:
                print(f"ID: {consulta[0]}")
                print(f"Propietario: {consulta[1]} (C.I.: {consulta[2]})")
                print(f"Teléfono: {consulta[3]} | Dirección: {consulta[4]}")
                print(f"Motivo: {consulta[5]}")
                print(f"Mascota: {consulta[6]} | Especie: {consulta[7]} | Raza: {consulta[8]}")
                print(f"Sexo: {consulta[9]} | Edad: {consulta[10]} años | Pelaje: {consulta[11]}")
                print(f"C.C.: {consulta[12]} | Desparasitaciones: {consulta[13]}")
                print(f"Vacuna: {consulta[14]} | Alimentación: {consulta[15]}")
                print(f"Enfermedad: {consulta[16]} | Tratamiento: {consulta[17]}")
                print(f"Anamnesis: {consulta[18]}")
                print(f"Fecha: {consulta[19]}")
                print(f"{'-'*60}")
        else:
            print("No hay registros en la tabla 'consultas'.")
            
    except Exception as e:
        print(f"Error al leer los datos: {e}")
# Insertar en la base de datos
connection = QueriesSQLite.create_connection("pdvDB.sqlite")
#insertar_consulta(connection, consulta_data)
#Para mostrar estructura:
#cursor = connection.cursor()
#cursor.execute("PRAGMA table_info(consultas);")
#columns = cursor.fetchall()
#for col in columns:
 #  print(col)
   
   
   
#imprimir_todas_las_consultas()