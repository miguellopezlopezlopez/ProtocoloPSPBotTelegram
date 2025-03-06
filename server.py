import socket
import threading

# Configuración del servidor
HOST = '0.0.0.0'  # Escucha en todas las interfaces
PORT = 2000  # Puerto fijo

clientes = []

def manejar_cliente(cliente, direccion):
    """Maneja la comunicación con un cliente."""
    print(f"[+] Nueva conexión desde {direccion}")
    clientes.append(cliente)

    try:
        while True:
            mensaje = cliente.recv(1024).decode('utf-8')
            if not mensaje:
                break
            print(f"[Mensaje recibido] {direccion}: {mensaje}")
            retransmitir_mensaje(mensaje, cliente)
    except:
        pass
    finally:
        print(f"[-] Cliente {direccion} desconectado")
        clientes.remove(cliente)
        cliente.close()

def retransmitir_mensaje(mensaje, remitente):
    """Envía el mensaje a todos los clientes excepto al remitente."""
    for cliente in clientes:
        if cliente != remitente:
            try:
                cliente.send(mensaje.encode('utf-8'))
            except:
                cliente.close()
                clientes.remove(cliente)

# Configuración del socket del servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen()

print(f"🟢 Servidor escuchando en {HOST}:{PORT}")

while True:
    cliente, direccion = servidor.accept()
    hilo = threading.Thread(target=manejar_cliente, args=(cliente, direccion))
    hilo.start()
