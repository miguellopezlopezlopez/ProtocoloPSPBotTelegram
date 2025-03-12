import socket
import asyncio
from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configuración del bot de Telegram
TOKEN = ""  #Reemplaza con el token de tu Bot
CHAT_ID_GRUPO = ""  # Reemplaza con el ID del chat de Telegram

# Configuración del servidor TCP
SERVER_IP = "127.0.0.1"  # Cambia si el servidor está en otra máquina
PORT = 2000

class BotTelegramCliente:
    def __init__(self):
        """Se conecta al servidor TCP como un cliente más."""
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.setblocking(False)  # Hacer el socket no bloqueante
        
        # Diccionario para mapear mensajes entre Telegram y el chat local
        self.mensajes_telegram = {}  # {id_mensaje_telegram: texto_mensaje}
        
        try:
            self.cliente.connect_ex((SERVER_IP, PORT))
            print("🤖 Bot conectado al servidor de chat.")
        except Exception as e:
            print(f"❌ Error al conectar con el servidor: {e}")
            return

    async def escuchar_mensajes(self):
        """Escucha los mensajes del servidor y los reenvía a Telegram."""
        while True:
            try:
                # Usamos asyncio para esperar datos en el socket no bloqueante
                data = await asyncio.get_event_loop().sock_recv(self.cliente, 1024)
                mensaje = data.decode('utf-8')
                if mensaje:
                    print(f"[Chat TCP] {mensaje}")
                    # Enviar el mensaje a Telegram
                    sent_message = await self.enviar_a_telegram(mensaje)
                    # Guardar referencia al mensaje para posibles respuestas
                    if sent_message:
                        self.mensajes_telegram[sent_message.message_id] = mensaje
                await asyncio.sleep(0.1)  # Pequeña pausa para no saturar la CPU
            except Exception as e:
                print(f"⚠️ Error al recibir mensaje: {e}")
                await asyncio.sleep(1)  # Espera antes de reintentar

    async def enviar_a_servidor(self, mensaje, replied_to=None):
        """Envía mensajes de Telegram al servidor TCP."""
        try:
            # Si es respuesta a un mensaje, formatear adecuadamente
            if replied_to and replied_to in self.mensajes_telegram:
                mensaje_original = self.mensajes_telegram[replied_to]
                mensaje = f"[RESPUESTA a '{mensaje_original}'] {mensaje}"
                
            await asyncio.get_event_loop().sock_sendall(self.cliente, mensaje.encode('utf-8'))
        except Exception as e:
            print(f"⚠️ No se pudo enviar el mensaje al servidor: {e}")

    async def enviar_a_telegram(self, mensaje):
        """Envía un mensaje del servidor al grupo de Telegram."""
        try:
            return await self.app.bot.send_message(chat_id=CHAT_ID_GRUPO, text=mensaje)
        except Exception as e:
            print(f"⚠️ Error al enviar mensaje a Telegram: {e}")
            return None

    async def start(self, update: Update, context: CallbackContext):
        """Maneja el comando /start en Telegram."""
        await update.message.reply_text("¡Soy un bot que retransmite mensajes del chat en tiempo real! Puedes responder a cualquier mensaje y se enviará como respuesta.")

    async def recibir_mensaje(self, update: Update, context: CallbackContext):
        """Cuando un usuario de Telegram escribe, envía el mensaje al servidor TCP."""
        mensaje = f"Telegram - {update.message.from_user.first_name}: {update.message.text}"
        print(f"[Telegram] {mensaje}")
        
        # Verificar si es una respuesta a otro mensaje
        replied_to = None
        if update.message.reply_to_message:
            replied_to = update.message.reply_to_message.message_id
            
        await self.enviar_a_servidor(mensaje, replied_to)

    async def run(self):
        """Método principal que coordina todas las tareas."""
        # Configurar el bot de Telegram
        self.app = Application.builder().token(TOKEN).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.recibir_mensaje))
        
        print("🤖 Bot de Telegram iniciado...")
        
        # Crear tarea para escuchar mensajes del servidor
        asyncio.create_task(self.escuchar_mensajes())
        
        # Iniciar el bot de Telegram
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
        # Mantener el bot ejecutándose
        try:
            # Mantener el programa funcionando
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            # Cerrar correctamente
            await self.app.stop()
            await self.app.shutdown()

# Punto de entrada principal
if __name__ == "__main__":
    bot = BotTelegramCliente()
    
    # Configurar y ejecutar el bucle de eventos
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("🔴 Bot detenido manualmente.")
