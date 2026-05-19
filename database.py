import sqlite3

#Nombre de la base de datos
DATA_BASE = "agencia_viajes.db"

#funcion para guardar interacciones de los usuarios
def guardar_interaccion(usuario: str, mensaje: str, respuesta: str):
    """ Funcion encargada de insertar los datos del chat en la base de datos 
    El campo 'fecha_consulta' se llena automáticamente con la fecha y hora actual."""

    conn = None
    try:
        #1. Conectar a la base de datos
        conn = sqlite3.connect(DATA_BASE)
        cursor = conn.cursor()

        #2. Sentencia SQL con marcadores de posición por seguridad (asi evitamos inyecciones SQL)
        query = """
        INSERT INTO consultas_viajes (usuario_telegram, mensaje_cliente, respuesta_ia)
        VALUES (?, ?, ?);
        """
        #3. Ejecuta la sentencia pasando por los datos reales como tupla
        cursor.execute(query, (usuario, mensaje, respuesta))

        #4. Confirmar la operacion en el archivo de la base de datos
        conn.commit()
        print(f"💾 [DB Success] Registro guardado para el usuario: {usuario}")

    except sqlite3.Error as e:
        print(f"💾 [DB Error] Error al guardar el registro para el usuario: {usuario}")
        print(f"💾 [DB Error] Detalles: {e}")
        
    finally:
        if conn:
            conn.close()