import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import time

# Configuración del cliente
SERVER_IP = "127.0.0.1"  # Cambia esto si el servidor está en otra máquina
PORT = 2000

class ClienteChat:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat en Tiempo Real")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.resizable(True, True)
        
        # Configurar grid para que la ventana sea redimensionable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        
        # Inicializar variables
        self.conectado = False
        self.cliente = None

        # Configurar la interfaz
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.text_area.config(state=tk.DISABLED)

        frame_entry = tk.Frame(self.root)
        frame_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        frame_entry.columnconfigure(0, weight=1)

        self.entry_mensaje = tk.Text(frame_entry, height=4, font=("Arial", 12))
        self.entry_mensaje.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.boton_enviar = tk.Button(frame_entry, text="Enviar", command=self.enviar_mensaje, font=("Arial", 12))
        self.boton_enviar.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.entry_mensaje.bind("<Return>", self.enviar_con_enter)
        self.entry_mensaje.bind("<Shift-Return>", self.nueva_linea)
        
        # Manejar cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        # Obtener nombre de usuario
        self.nombre_usuario = simpledialog.askstring("Nombre de usuario", "Ingresa tu nombre:")
        if not self.nombre_usuario:
            self.nombre_usuario = f"Usuario_{int(time.time()) % 1000}"  # Nombre por defecto
            messagebox.showinfo("Información", f"Se asignó el nombre: {self.nombre_usuario}")

        # Conectar al servidor
        self.conectar_al_servidor()

    def conectar_al_servidor(self):
        """Establece conexión con el servidor"""
        try:
            self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente.connect((SERVER_IP, PORT))
            self.cliente.send(f"{self.nombre_usuario} se ha unido al chat.".encode('utf-8'))
            self.conectado = True
            self.mostrar_mensaje(f"✅ Conectado al servidor como {self.nombre_usuario}")
            
            # Iniciar hilo para recibir mensajes
            hilo = threading.Thread(target=self.recibir_mensajes, daemon=True)
            hilo.start()
        except Exception as e:
            self.mostrar_mensaje(f"❌ No se pudo conectar al servidor: {e}")
            # Intentar reconectar en 5 segundos
            self.root.after(5000, self.conectar_al_servidor)

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje en la interfaz de forma segura."""
        # Esta función es segura para llamar desde cualquier hilo
        def _mostrar():
            self.text_area.config(state=tk.NORMAL)
            self.text_area.insert(tk.END, mensaje + "\n")
            self.text_area.config(state=tk.DISABLED)
            self.text_area.yview(tk.END)
        
        # Si es el hilo principal, ejecutar directamente
        if threading.current_thread() is threading.main_thread():
            _mostrar()
        else:
            # Si no, programar en la cola de eventos de Tkinter
            self.root.after(0, _mostrar)

    def enviar_mensaje(self):
        """Envía un mensaje al servidor."""
        mensaje = self.entry_mensaje.get("1.0", tk.END).strip()
        if mensaje and self.conectado:
            try:
                mensaje_formateado = f"{self.nombre_usuario}: {mensaje}"
                self.cliente.send(mensaje_formateado.encode('utf-8'))
                
                # Mostrar el mensaje localmente con formato diferenciado
                self.mostrar_mensaje(f"Tú: {mensaje}")
                
                self.entry_mensaje.delete("1.0", tk.END)  # Limpiar entrada
            except Exception as e:
                self.mostrar_mensaje(f"⚠️ No se pudo enviar el mensaje: {e}")
                self.conectado = False
                self.root.after(5000, self.conectar_al_servidor)  # Intentar reconectar

    def enviar_con_enter(self, event):
        """Envía mensaje con Enter"""
        self.enviar_mensaje()
        return "break"  # Evita que se inserte un salto de línea

    def nueva_linea(self, event):
        """Permite nueva línea con Shift+Enter"""
        return None  # Permite el comportamiento normal de Shift+Enter

    def recibir_mensajes(self):
        """Recibe mensajes del servidor y los muestra en la interfaz."""
        while self.conectado:
            try:
                mensaje = self.cliente.recv(1024).decode('utf-8')
                if not mensaje:
                    # Si no hay mensaje, el servidor probablemente cerró la conexión
                    raise ConnectionError("Conexión cerrada por el servidor")
                
                # Filtrar mensajes propios para evitar duplicados
                # Solo mostrar mensajes que no sean tuyos
                if not mensaje.startswith(f"{self.nombre_usuario}: "):
                    self.mostrar_mensaje(mensaje)
            except Exception as e:
                self.mostrar_mensaje(f"⚠️ Error de conexión: {e}")
                self.conectado = False
                # Intentar reconectar desde el hilo principal
                self.root.after(5000, self.conectar_al_servidor)
                break

    def cerrar_aplicacion(self):
        """Maneja el cierre de la aplicación correctamente."""
        if self.conectado:
            try:
                # Enviar mensaje de despedida
                self.cliente.send(f"{self.nombre_usuario} ha abandonado el chat.".encode('utf-8'))
                self.cliente.close()
            except:
                pass  # Ignorar errores al cerrar
        self.root.destroy()

# Iniciar cliente con Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    cliente = ClienteChat(root)
    root.mainloop()