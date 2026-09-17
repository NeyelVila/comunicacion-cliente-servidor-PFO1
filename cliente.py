import socket
import sys

# Misma configuración que en el servidor
HOST = 'localhost'
PORT = 5500


def iniciar_cliente():
    """Conecta al servidor y permite enviar múltiples preguntas."""
    cliente = None

    try:
        # Creación del socket TCP
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((HOST, PORT))
        print("=" * 65)
        print(f"✅ Conectado al servidor en {HOST}:{PORT}")
        print("💡 Escribí tu pregunta o 'menu' para ver las opciones disponibles.")
        print("🛑 Escribí 'éxito' para finalizar la conexión.")
        print("=" * 65 + "\n")

        while True:
            pregunta = input("Escribe tu pregunta: ").strip()

            if not pregunta:
                continue

            # Condición de salida
            if pregunta.lower() in ('éxito', 'exito'):
                print("[SALIENDO] Finalizando sesión...")
                break

            # Enviamos pregunta codificada al servidor
            cliente.sendall(pregunta.encode('utf-8'))

            # Recibir la confirmación y respuesta del servidor
            respuesta = cliente.recv(1024).decode('utf-8')
            print(f"Servidor: {respuesta}\n")

    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar al servidor en {HOST}:{PORT}.")
        print("Asegúrate de que 'server.py' esté en ejecución antes de iniciar el cliente.")
    except KeyboardInterrupt:
        print("\n[CANCELADO] Sesión interrumpida.")
    finally:
        cliente.close()
        print("[CONEXIÓN] Socket del cliente cerrado.")


if __name__ == '__main__':
    iniciar_cliente()