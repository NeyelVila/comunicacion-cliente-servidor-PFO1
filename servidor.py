import socket
import sqlite3
from datetime import datetime
import sys

# Configuración del servidor y persistencia
HOST = 'localhost'
PORT = 5500
DB_PATH = 'chat.db'

# Base de conocimiento (Preguntas frecuentes y respuestas)
PREGUNTAS_RESPUESTAS = {
    "¿cuál es la capital de francia?": "París",
    "¿cuantos lados tiene un cuadrado?": "4",
    "¿cuántos lados tiene un cuadrado?": "4",
    "¿qué lenguaje usamos?": "Python",
    "¿que lenguaje usamos?": "Python",
    "menu": "Consultas disponibles: ¿Cuál es la capital de Francia? | ¿Cuántos lados tiene un cuadrado? | ¿Qué lenguaje usamos?",
    "ayuda": "Consultas disponibles: ¿Cuál es la capital de Francia? | ¿Cuántos lados tiene un cuadrado? | ¿Qué lenguaje usamos?"
}


def inicializar_db(nombre_db: str = DB_PATH):
    """
    Crea la base de datos y la tabla 'mensajes' si no existen.
    Maneja excepciones en caso de que la DB no sea accesible por permisos o disco.
    """
    try:
        conexion = sqlite3.connect(nombre_db)
        cursor = conexion.cursor()
        
        # Estructura requerida: id, contenido, fecha_envio, ip_cliente
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        ''')
        conexion.commit()
        conexion.close()
        print(f"[DB] Base de datos '{nombre_db}' inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"[ERROR DB] No se pudo acceder a la base de datos: {e}")
        sys.exit(1)


def guardar_mensaje(contenido: str, ip_cliente: str, nombre_db: str = DB_PATH) -> str:
    """
    Registra cada mensaje recibido en la base de datos SQLite.
    Retorna la marca de tiempo generada.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conexion = sqlite3.connect(nombre_db)
        cursor = conexion.cursor()
        
        # Inserción parametrizada para prevenir inyección SQL
        cursor.execute('''
            INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
            VALUES (?, ?, ?)
        ''', (contenido, timestamp, ip_cliente))
        
        conexion.commit()
        conexion.close()
        return timestamp
    except sqlite3.Error as e:
        print(f"[ERROR DB] Error al persistir el mensaje: {e}")
        return timestamp


def buscar_respuesta(pregunta: str) -> str:
    """Busca coincidencias en el diccionario sin distinguir mayúsculas."""
    clave = pregunta.strip().lower()
    return PREGUNTAS_RESPUESTAS.get(clave, "No tengo esa respuesta registrada. Escribí 'menu' para ver las preguntas disponibles.")


def inicializar_socket(host: str, puerto: int) -> socket.socket:
    """
    Configura y enlaza el socket TCP/IP.
    Maneja el error en caso de que el puerto ya esté en uso.
    """
    try:
        # Configuración del socket TCP (IPv4 + Stream)
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # SO_REUSEADDR evita el bloqueo del socket tras un reinicio inmediato
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, puerto))
        servidor.listen(5)
        print(f"[SERVIDOR] Escuchando en {host}:{puerto}...")
        return servidor
    except OSError as e:
        # Captura de error de puerto ocupado (EADDRINUSE)
        print(f"[ERROR RED] No se pudo abrir el puerto {puerto}. Posible puerto ocupado: {e}")
        sys.exit(1)


def atender_cliente(cliente_socket: socket.socket, direccion: tuple):
    """
    Acepta y procesa múltiples mensajes del cliente hasta que este se desconecta.
    """
    ip_cliente = direccion[0]
    print(f"[CONEXIÓN] Cliente conectado desde {direccion}")

    try:
        while True:
            datos = cliente_socket.recv(1024)
            if not datos:
                break

            mensaje = datos.decode('utf-8').strip()
            print(f"[{ip_cliente}] Pregunta: {mensaje}")

            # 1. Guardar en SQLite
            timestamp = guardar_mensaje(mensaje, ip_cliente)

            # 2. Obtener respuesta del combo de preguntas
            respuesta_bot = buscar_respuesta(mensaje)

            # 3. Responder con la confirmación obligatoria + la respuesta encontrada
            respuesta_final = f"Mensaje recibido: {timestamp} | Respuesta: {respuesta_bot}"
            cliente_socket.sendall(respuesta_final.encode('utf-8'))

    except ConnectionResetError:
        print(f"[CONEXIÓN] El cliente {direccion} se desconectó inesperadamente.")
    finally:
        cliente_socket.close()
        print(f"[DESCONEXIÓN] Sesión finalizada con {direccion}")


def ejecutar_servidor():
    """Bucle principal de ejecución del servidor."""
    inicializar_db()
    servidor_socket = inicializar_socket(HOST, PORT)

    try:
        while True:
            # Espera nuevas conexiones
            cliente_socket, direccion = servidor_socket.accept()
            atender_cliente(cliente_socket, direccion)
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Servidor detenido manualmente.")
    finally:
        servidor_socket.close()
        print("[SERVIDOR] Socket cerrado.")


if __name__ == '__main__':
    ejecutar_servidor()