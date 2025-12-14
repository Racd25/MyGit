import sqlite3
from sqlite3 import Error

class QueriesSQLite:
    def create_connection(path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    def execute_query(connection, query, data_tuple):
        cursor = connection.cursor()
        try:
            cursor.execute(query, data_tuple)
            connection.commit()
            print("Query executed successfully")
            return cursor.lastrowid
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query(connection, query, data_tuple=()):
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query,data_tuple)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")

    def create_tables():
       connection = QueriesSQLite.create_connection("pdvDB.sqlite")

       tabla_consultas = """
            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_propietario TEXT NOT NULL,
                ci TEXT NOT NULL UNIQUE,
                telefono TEXT,
                direccion TEXT,
                motivo_consulta TEXT,
                nombre_mascota TEXT,
                especie TEXT,
                raza TEXT,
                sexo TEXT,
                edad REAL,
                pelaje TEXT,
                cc TEXT,
               
                enfermedad TEXT,
                tratamiento TEXT,

                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

       tabla_examen_clinico = """
                CREATE TABLE IF NOT EXISTS examen_clinico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_consulta INTEGER NOT NULL,
                    desparasitaciones TEXT,
                    vacuna TEXT,
                    alimentacion TEXT,
                    anamnesis TEXT,
                    peso REAL NOT NULL,
                    temperatura REAL NOT NULL,
                    fc TEXT,
                    fr TEXT,
                    p_femoral TEXT,
                    yugular TEXT,
                    tpg TEXT,
                    ps TEXT,
                    pd TEXT,
                    pam TEXT,
                    mucosas TEXT,
                    ganglios TEXT,
                    palp_abdominal TEXT,
                    patron_lesion TEXT,
                    genitales TEXT,
                    procedimiento_diagnos TEXT,
                    pruebas_comple TEXT,
                    diag_diferencial TEXT,
                    diag_definitivo TEXT,
                    tratamiento_apli TEXT,
                    tratamiento_indi TEXT,
                    proxi_consulta DATE,
                    fecha_examen DATE,

                    -- Fila 2
                    lab TEXT,
                    hb TEXT,
                    eosi TEXT,
                    urea TEXT,
                    alt TEXT,
                    otras_20 TEXT,
                    -- Fila 3
                    hto TEXT,
                    plaq TEXT,
                    creat TEXT,
                    ast TEXT,
                    otras_30 TEXT,
                    -- Fila 4
                    leuc TEXT,
                    vcm TEXT,
                    bun TEXT,
                    fa TEXT,
                    otras_40 TEXT,
                    -- Fila 5
                    neut TEXT,
                    hcm TEXT,
                    pt TEXT,
                    bt TEXT,
                    otras_50 TEXT,
                    -- Fila 6
                    lint TEXT,
                    chcm TEXT,
                    alb TEXT,
                    bi TEXT,
                    otras_60 TEXT,
                    --Fila 7
                    mon TEXT,
                    descar TEXT,
                    glo TEXT,
                    bd TEXT,
                    otras_70 TEXT,
                    FOREIGN KEY(id_consulta) REFERENCES consultas(id)
                );
                        """


       create_historia_der = """
            CREATE TABLE IF NOT EXISTS historia_dermatologica (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_consulta INTEGER NOT NULL,
                fecha_registro DATE DEFAULT CURRENT_TIMESTAMP,
                
                -- Datos básicos
                prurito_escala INTEGER,
                control_ectoparasitos TEXT,
                otros_animales_afectados TEXT,
                estilo_vida TEXT,
                paseos TEXT,
                banos TEXT,
                frecuencia TEXT,
                productos_usados TEXT,
                tratamientos_previos TEXT,
                examen_fisico TEXT,
                estado_actual TEXT,
                
                -- Patrón de distribución
                simetrico TEXT,
                asimetrico TEXT,
                generalizado TEXT,
                focal TEXT,
                multifocal TEXT,
                regional TEXT,
                
                -- Lesiones primarias (CheckBoxes)
                grid1 BOOLEAN DEFAULT 0,  -- ALOPECIA
                grid2 BOOLEAN DEFAULT 0,  -- NÓDULO
                grid3 BOOLEAN DEFAULT 0,  -- AMPOLLA
                grid4 BOOLEAN DEFAULT 0,  -- PÁPULA
                grid5 BOOLEAN DEFAULT 0,  -- ERITEMA
                grid6 BOOLEAN DEFAULT 0,  -- PÓSTULA
                grid7 BOOLEAN DEFAULT 0,  -- MANCHA
                grid8 BOOLEAN DEFAULT 0,  -- VESÍCULA
                grid9 BOOLEAN DEFAULT 0,  -- MÁCULA
                grid10 BOOLEAN DEFAULT 0, -- TUMOR
                
                -- Lesiones secundarias (CheckBoxes)
                grid11 BOOLEAN DEFAULT 0, -- ABSCESO
                grid12 BOOLEAN DEFAULT 0, -- ÚLCERA
                grid13 BOOLEAN DEFAULT 0, -- COLLARÍN EPIDÉRMICO
                grid14 BOOLEAN DEFAULT 0, -- QUISTE
                grid15 BOOLEAN DEFAULT 0, -- COSTRA
                grid16 BOOLEAN DEFAULT 0, -- PIGMENTACIÓN HIPER
                grid17 BOOLEAN DEFAULT 0, -- EROSIÓN
                grid18 BOOLEAN DEFAULT 0, -- CICATRIZ
                grid19 BOOLEAN DEFAULT 0, -- PIGMENTACIÓN HIPO
                grid20 BOOLEAN DEFAULT 0, -- ESCAMA
                grid21 BOOLEAN DEFAULT 0, -- CALLO
                grid22 BOOLEAN DEFAULT 0, -- QUERATOSIS HIPER   
                grid23 BOOLEAN DEFAULT 0, -- LIQUENIFICACION
                grid24 BOOLEAN DEFAULT 0, -- QUERATOSIS HIPO
                
                
                diag_diferencial TEXT,
                
                
                anagen TEXT,
                teogen TEXT, 
                tricomexis TEXT,
                melanina TEXT,
                demodex TEXT,
                
                tricografia TEXT,
                
                lampara_woo TEXT,
                
                agentes TEXT,
                cabeza TEXT,
                cuello TEXT,
                abdomen TEXT,
                dd TEXT,
                di TEXT,
                pd TEXT,
                pi TEXT,
                otras TEXT,
                
                notas TEXT,
                
                FOREIGN KEY (id_consulta) REFERENCES consultas (id)
            )
            """


       tabla_usuarios = """
    CREATE TABLE IF NOT EXISTS usuarios(
        username TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        password TEXT NOT NULL,
        tipo TEXT NOT NULL
    );
    """
    
       tabla_vets = """
    CREATE TABLE IF NOT EXISTS veterinarios(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CI2 INTEGER,
        Nombre TEXT,
        CMVB TEXT NOT NULL,
        MPPS TEXT NOT NULL
    );
    """
    
       tabla_recipes = """
    CREATE TABLE IF NOT EXISTS recipes(
        ID INTEGER PRIMARY KEY AUTOINCREMENT ,
        id_consulta INTEGER NOT NULL,
        CI INTEGER NOT NULL,
        Nombre TEXT,
        CMVB TEXT NOT NULL,
        MPPS TEXT NOT NULL,
        Paciente TEXT NOT NULL,
        rp TEXT NOT NULL,
        ind TEXT NOT NULL,
        fecha DATE
    );
    """


 
       QueriesSQLite.execute_query(connection, tabla_consultas, ())
       QueriesSQLite.execute_query(connection, tabla_usuarios, ())
       QueriesSQLite.execute_query(connection, tabla_examen_clinico, ())
       QueriesSQLite.execute_query(connection, create_historia_der, ())
       QueriesSQLite.execute_query(connection, tabla_vets, ())
       QueriesSQLite.execute_query(connection, tabla_recipes, ())



       

if __name__ == "__main__":
    from datetime import datetime, timedelta

    connection = QueriesSQLite.create_connection("pdvDB.sqlite")

    # Actualizar una fecha de venta específica
    fecha1 = datetime.today() - timedelta(days=5)
    nueva_data = (fecha1, 4)
    QueriesSQLite.create_tables()

    actualizar = """
    UPDATE
        ventas
    SET
        fecha = ?
    WHERE
        id = ?
    """

    QueriesSQLite.execute_query(connection, actualizar, nueva_data)
    

    # Leer ventas
'''

-- También modifica la tabla de items_venta para identificar el tipo
ALTER TABLE items_venta ADD COLUMN tipo_item TEXT DEFAULT 'producto';
-- 'producto' para productos con stock, 'servicio' para servicios
    create_product_table = """
    CREATE TABLE IF NOT EXISTS productos(
    codigo TEXT PRIMARY KEY, 
    nombre TEXT NOT NULL, 
    precio REAL NOT NULL, 
    cantidad INTEGER NOT NULL
    );
    """
    QueriesSQLite.execute_query(connection, create_product_table, tuple()) 


    create_user_table = """
     CREATE TABLE IF NOT EXISTS usuarios(
      username TEXT PRIMARY KEY, 
      nombre TEXT NOT NULL, 
      password TEXT NOT NULL,
      tipo TEXT NOT NULL
       );
     """
    QueriesSQLite.execute_query(connection, create_user_table, tuple()) 


    crear_producto = """
    INSERT INTO
       productos (codigo, nombre, precio, cantidad)
     VALUES
         ('111', 'leche 1l', 20.0, 20),
         ('222', 'cereal 500g', 50.5, 15), 
         ('333', 'yogurt 1L', 25.0, 10),
         ('444', 'helado 2L', 80.0, 20),
         ('555', 'alimento para perro 20kg', 750.0, 5),
         ('666', 'shampoo', 100.0, 25),
         ('777', 'papel higiénico 4 rollos', 35.5, 30),
        ('888', 'jabón para trastes', 65.0, 5)
     """
    QueriesSQLite.execute_query(connection, crear_producto, tuple()) 

    select_products = "SELECT * from productos"
    productos = QueriesSQLite.execute_read_query(connection, select_products)
    for producto in productos:
        print(producto)


    usuario_tuple=('admin', 'Persona 1', 'abc', 'admin')
    crear_usuario = """
    INSERT INTO
      usuarios (username, nombre, password, tipo)
    VALUES
        (?,?,?,?);
    """
    QueriesSQLite.execute_query(connection, crear_usuario, usuario_tuple) 


    # select_users = "SELECT * from usuarios"
    # usuarios = QueriesSQLite.execute_read_query(connection, select_users)
    # for usuario in usuarios:
    #     print("type:", type(usuario), "usuario:",usuario)

    # neuva_data=('Persona 55', '123', 'admin', 'persona1')
    # actualizar = """
    # UPDATE
    #   usuarios
    # SET
    #   nombre=?, password=?, tipo = ?
    # WHERE
    #   username = ?
    # """
    # QueriesSQLite.execute_query(connection, actualizar, neuva_data)

    # select_users = "SELECT * from usuarios"
    # usuarios = QueriesSQLite.execute_read_query(connection, select_users)
    # for usuario in usuarios:
    #     print("type:", type(usuario), "usuario:",usuario)



    # select_products = "SELECT * from productos"
    # productos = QueriesSQLite.execute_read_query(connection, select_products)
    # for producto in productos:
    #     print(producto)

    select_users = "SELECT * from usuarios"
    usuarios = QueriesSQLite.execute_read_query(connection, select_users)
    for usuario in usuarios:
        print("type:", type(usuario), "usuario:",usuario)

    # producto_a_borrar=('888',)
    # borrar = """DELETE from productos where codigo = ?"""
    # QueriesSQLite.execute_query(connection, borrar, producto_a_borrar)

    # select_products = "SELECT * from productos"
    # productos = QueriesSQLite.execute_read_query(connection, select_products)
    # for producto in productos:
    #     print(producto)
'''
