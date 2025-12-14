from sqlqueries import QueriesSQLite

def siguiente(self):
    # Validación de ids
    if not hasattr(self, 'ids') or not self.ids:
        print("Los IDs no están disponibles todavía.")
        return

    nombre_propietario = "sdas"
    ci = "sdas"
    telefono = "sdas"
    direccion = "sdas"
    motivo_consulta ="sdas"
    nombre_mascota = "sdas"
    especie = "sdas"
    raza = "sdas"
    sexo = "sdas"
    edad = "sdas"
    pelaje = "sdas"
    cc ="sdas"
    enfermedad = "sdas"
    tratamiento = self.ids.tratamiento.text.strip()

    # Validación básica
    if not nombre_propietario or not ci:
        if hasattr(self.ids, 'notificacion'):
            self.ids.notificacion.text = "Por favor, completa los campos obligatorios"
        else:
            print("Advertencia: No se encontró el id 'notificacion'")
        return
    else:
        if hasattr(self.ids, 'notificacion'):
            self.ids.notificacion.text = ""


    # Preparar datos
    consulta_data = (
        nombre_propietario,
        ci,
        telefono,
        direccion,
        motivo_consulta,
        nombre_mascota,
        especie,
        raza,
        sexo,
        edad,
        pelaje,
        cc,
        enfermedad,
        tratamiento,
    )

    # Guardar en la base de datos
    connection = QueriesSQLite.create_connection("pdvDB.sqlite")

    insert_query = """
    INSERT INTO consultas (
        nombre_propietario, ci, telefono, direccion, motivo_consulta,
        nombre_mascota, especie, raza, sexo, edad, pelaje, cc,
        enfermedad, tratamiento
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,)
    """

    QueriesSQLite.execute_query(connection, insert_query, consulta_data)

    print("Consulta guardada correctamente")