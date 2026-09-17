import socket
import sqlite3
from datetime import datetime
import sys
import threading

# Configuración del servidor y persistencia
HOST = "localhost"
PORT = 5500
DB_PATH = "chat.db"

# Base de conocimiento (Preguntas frecuentes y respuestas)
PREGUNTAS_RESPUESTAS = {
    "¿cuál es la capital de francia?": "París",
    "¿cuantos lados tiene un cuadrado?": "4",
    "¿cuántos lados tiene un cuadrado?": "4",
    "¿qué lenguaje usamos?": "Python",
    "¿que lenguaje usamos?": "Python",
    "menu": "Consultas disponibles: ¿Cuál es la capital de Francia? | ¿Cuántos lados tiene un cuadrado? | ¿Qué lenguaje usamos?",
    "ayuda": "Consultas disponibles: ¿Cuál es la capital de Francia? | ¿Cuántos lados tiene un cuadrado? | ¿Qué lenguaje usamos?",
}

# SQLite permite múltiples conexiones, pero serializamos las escrituras
# para evitar problemas cuando hay varios clientes simultáneos.
DB_LOCK = threading.Lock()


def inicializar_db(nombre_db: str = DB_PATH):
    """Crea la base de datos y adapta una BD existente al nuevo esquema."""
    try:
        with sqlite3.connect(nombre_db) as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    respuesta TEXT,
                    fecha_envio TEXT NOT NULL,
                    ip_cliente TEXT NOT NULL
                )
            """)

            # Compatibilidad con un chat.db creado por la versión anterior.
            cursor.execute("PRAGMA table_info(mensajes)")
            columnas = {fila[1] for fila in cursor.fetchall()}

            if "respuesta" not in columnas:
                cursor.execute("ALTER TABLE mensajes ADD COLUMN respuesta TEXT")

            conexion.commit()

        print(f"[DB] Base de datos '{nombre_db}' inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"[ERROR DB] No se pudo acceder a la base de datos: {e}")
        sys.exit(1)


def guardar_mensaje(
    contenido: str,
    respuesta: str,
    ip_cliente: str,
    nombre_db: str = DB_PATH
) -> str:
    """
    Guarda en un único registro:
    - consulta enviada por el cliente
    - respuesta generada por el servidor
    - fecha/hora
    - IP del cliente
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with DB_LOCK:
            with sqlite3.connect(nombre_db) as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO mensajes
                        (contenido, respuesta, fecha_envio, ip_cliente)
                    VALUES (?, ?, ?, ?)
                """, (contenido, respuesta, timestamp, ip_cliente))
                conexion.commit()

        return timestamp

    except sqlite3.Error as e:
        print(f"[ERROR DB] Error al persistir el mensaje: {e}")
        return timestamp


def buscar_respuesta(pregunta: str) -> str:
    """Busca una respuesta en la base de conocimiento sin distinguir mayúsculas."""
    clave = pregunta.strip().lower()
    return PREGUNTAS_RESPUESTAS.get(
        clave,
        "No tengo esa respuesta registrada. Escribí 'menu' para ver las preguntas disponibles."
    )


def inicializar_socket(host: str, puerto: int) -> socket.socket:
    """Configura y enlaza el socket TCP/IP."""
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, puerto))
        servidor.listen(5)
        print(f"[SERVIDOR] Escuchando en {host}:{puerto}...")
        return servidor

    except OSError as e:
        print(f"[ERROR RED] No se pudo abrir el puerto {puerto}. Posible puerto ocupado: {e}")
        sys.exit(1)


def atender_cliente(cliente_socket: socket.socket, direccion: tuple):
    """Atiende a un cliente y procesa múltiples consultas."""
    ip_cliente = direccion[0]
    print(f"[CONEXIÓN] Cliente conectado desde {direccion}")

    try:
        while True:
            datos = cliente_socket.recv(4096)

            if not datos:
                break

            mensaje = datos.decode("utf-8").strip()

            if not mensaje:
                continue

            print(f"[{ip_cliente}] Consulta recibida: {mensaje}")

            # 1. El servidor genera su respuesta.
            respuesta_servidor = buscar_respuesta(mensaje)

            # 2. Se guardan CONSULTA y RESPUESTA en el mismo registro.
            timestamp = guardar_mensaje(
                mensaje,
                respuesta_servidor,
                ip_cliente
            )

            # 3. El servidor devuelve su respuesta al cliente.
            respuesta_final = (
                f"Mensaje recibido: {timestamp}\n"
                f"Respuesta del servidor: {respuesta_servidor}"
            )

            cliente_socket.sendall(respuesta_final.encode("utf-8"))

            print(f"[{ip_cliente}] Respuesta enviada: {respuesta_servidor}")

    except ConnectionResetError:
        print(f"[CONEXIÓN] El cliente {direccion} se desconectó inesperadamente.")
    except UnicodeDecodeError:
        print(f"[ERROR] Se recibió información no válida desde {direccion}.")
    finally:
        cliente_socket.close()
        print(f"[DESCONEXIÓN] Sesión finalizada con {direccion}")


def ejecutar_servidor():
    """Bucle principal del servidor. Permite múltiples clientes mediante hilos."""
    inicializar_db()
    servidor_socket = inicializar_socket(HOST, PORT)

    try:
        while True:
            cliente_socket, direccion = servidor_socket.accept()

            hilo = threading.Thread(
                target=atender_cliente,
                args=(cliente_socket, direccion),
                daemon=True
            )
            hilo.start()

    except KeyboardInterrupt:
        print("\n[SERVIDOR] Servidor detenido manualmente.")
    finally:
        servidor_socket.close()
        print("[SERVIDOR] Socket cerrado.")


if __name__ == "__main__":
    ejecutar_servidor()

