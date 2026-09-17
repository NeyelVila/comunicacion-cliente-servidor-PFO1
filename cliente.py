import socket

# Misma configuración que en el servidor
HOST = "localhost"
PORT = 5500


def iniciar_cliente():
    """Conecta al servidor y permite enviar múltiples preguntas."""
    cliente = None

    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((HOST, PORT))

        print("=" * 70)
        print(f"✅ Conectado al servidor en {HOST}:{PORT}")
        print("💡 Escribí tu pregunta o 'menu' para ver las opciones.")
        print("🛑 Escribí 'éxito' para finalizar la conexión.")
        print("=" * 70 + "\n")

        while True:
            pregunta = input("Escribe tu pregunta: ").strip()

            if not pregunta:
                continue

            if pregunta.lower() in ("éxito", "exito"):
                print("[SALIENDO] Finalizando sesión...")
                break

            cliente.sendall(pregunta.encode("utf-8"))

            respuesta = cliente.recv(4096)

            if not respuesta:
                print("[ERROR] El servidor cerró la conexión.")
                break

            print(f"\nServidor:\n{respuesta.decode('utf-8')}\n")

    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar al servidor en {HOST}:{PORT}.")
        print("Ejecutá primero 'servidor.py'.")

    except KeyboardInterrupt:
        print("\n[CANCELADO] Sesión interrumpida.")

    finally:
        if cliente is not None:
            cliente.close()
        print("[CONEXIÓN] Socket del cliente cerrado.")


if __name__ == "__main__":
    iniciar_cliente()
