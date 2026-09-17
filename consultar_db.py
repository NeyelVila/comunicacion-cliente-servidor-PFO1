"""
Herramienta de verificación de la base de datos SQLite.

Muestra tanto:
- la consulta enviada por el CLIENTE
- como la respuesta generada por el SERVIDOR

"""

import sqlite3
import os

DB_PATH = "chat.db"


def mostrar_mensajes():
    if not os.path.exists(DB_PATH):
        print(
            f"[AVISO] No se encontró el archivo '{DB_PATH}'. "
            "Ejecutá el servidor para crearlo."
        )
        return

    try:
        with sqlite3.connect(DB_PATH) as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id, contenido, respuesta, fecha_envio, ip_cliente
                FROM mensajes
                ORDER BY id ASC
            """)

            filas = cursor.fetchall()

        if not filas:
            print("[INFO] La base de datos está inicializada pero aún no contiene mensajes.")
            return

        print("=" * 120)
        print("                 REGISTRO DE COMUNICACIÓN CLIENTE ↔ SERVIDOR")
        print("=" * 120)

        for id_registro, contenido, respuesta, fecha, ip in filas:
            print(f"ID:                  {id_registro}")
            print(f"IP CLIENTE:          {ip}")
            print(f"FECHA Y HORA:        {fecha}")
            print(f"CONSULTA CLIENTE:    {contenido}")
            print(f"RESPUESTA SERVIDOR:  {respuesta or '[Sin respuesta registrada]'}")
            print("-" * 120)

        print("=" * 120)
        print(f"Total de registros: {len(filas)}")

    except sqlite3.OperationalError as e:
        print(f"[ERROR DB] La estructura de la base de datos no es compatible: {e}")
    except sqlite3.Error as e:
        print(f"[ERROR DB] Ocurrió un error al leer la base de datos: {e}")


if __name__ == "__main__":
    mostrar_mensajes()