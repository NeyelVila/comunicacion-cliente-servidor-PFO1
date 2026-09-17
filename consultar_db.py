"""
Permite comprobar de forma rápida que los mensajes se guarden correctamente
"""

import sqlite3
import os

DB_PATH = 'chat.db'

def mostrar_mensajes():
    if not os.path.exists(DB_PATH):
        print(f"[AVISO] No se encontró el archivo '{DB_PATH}'. Iniciá el servidor para crearlo.")
        return

    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT id, contenido, fecha_envio, ip_cliente FROM mensajes ORDER BY id ASC")
        filas = cursor.fetchall()
        conexion.close()

        if not filas:
            print("[INFO] La base de datos está inicializada pero aún no contiene mensajes.")
            return

        print("=" * 80)
        print(f"{'ID':<5} | {'IP CLIENTE':<16} | {'FECHA Y HORA':<20} | {'CONTENIDO'}")
        print("-" * 80)
        for fila in filas:
            print(f"{fila[0]:<5} | {fila[3]:<16} | {fila[2]:<20} | {fila[1]}")
        print("=" * 80)
        print(f"Total de registros: {len(filas)}")

    except sqlite3.Error as e:
        print(f"[ERROR DB] Ocurrió un error al leer la base de datos: {e}")

if __name__ == '__main__':
    mostrar_mensajes()
