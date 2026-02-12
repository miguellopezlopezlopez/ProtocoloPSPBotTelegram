# 📌 PROTOCOLO DE COMUNICACIÓN PARA CHAT EN TIEMPO REAL

## 📖 Introducción
Este sistema de chat en tiempo real basado en **Python** permite la comunicación entre múltiples clientes y la integración con Telegram. Se compone de tres elementos principales:

- **Servidor**: Maneja la comunicación entre los clientes.
- **Cliente**: Aplicación en Tkinter que permite a los usuarios enviar y recibir mensajes.
- **Bot de Telegram**: Conectado al servidor TCP, retransmite mensajes entre Telegram y el chat.

---

## ⚙️ Arquitectura del Sistema

### 🖥️ Servidor
El servidor actúa como un **intermediario**, recibiendo y retransmitiendo los mensajes entre los clientes.

- Utiliza **sockets TCP**.
- Maneja **múltiples conexiones** con `threading`.
- **Puerto de escucha**: `2000`.

### 🖥️ Cliente (Tkinter)
Cada cliente se conecta al servidor y permite:

- Enviar y recibir mensajes en una interfaz gráfica.
- Manejar reconexiones automáticas.
- Usar una **interfaz adaptable** en Tkinter.

### 🤖 Bot de Telegram
El bot de Telegram se conecta al servidor como un cliente más, permitiendo que:

- Los mensajes del chat TCP aparezcan en Telegram.
- Los mensajes de Telegram se reenvíen al chat TCP.
- Usa `asyncio` para eventos en tiempo real.

---

## 🔗 Protocolo de Comunicación

### 📌 Formato de Mensajes
Los mensajes siguen el formato:
```plaintext
nombre_usuario: mensaje
```
### 📌 Tipos de Mensajes
- `nombre_usuario: mensaje` → Enviar mensaje al chat.
- `nombre_usuario se ha unido al chat.` → Notificación de conexión.
- `nombre_usuario ha abandonado el chat.` → Notificación de desconexión.

---

## 📝 Explicación del Código

### **📌 Servidor (`server.py`)**
- Escucha en `0.0.0.0:2000`.
- Usa `threading` para múltiples clientes.
- Retransmite mensajes a todos los clientes.

### **📌 Cliente (`cliente.py`)**
- Interfaz en **Tkinter**.
- Reconexión automática.
- Soporta múltiples líneas con "Shift + Enter".

### **📌 Bot de Telegram (`bot.py`)**
- Conectado como cliente TCP.
- Recibe y envía mensajes entre el chat y Telegram.
- Usa `asyncio` para manejar eventos.

---

## 🚀 Instalación y Ejecución

### 🔧 Requisitos
- **Python 3.10+**
- Librerías necesarias:
```bash
pip install python-telegram-bot tk
```

### ▶️ Cómo Ejecutar
1️⃣ **Ejecutar el Servidor**
```bash
python server.py
```

2️⃣ **Ejecutar Clientes (pueden ser varios)**
```bash
python cliente.py
```

3️⃣ **Ejecutar el Bot de Telegram**
```bash
python bot.py
```

---

## 📌 Conclusión
Este sistema de chat permite la comunicación en tiempo real con integración en Telegram. Su arquitectura basada en **sockets TCP** lo hace rápido y eficiente.

Se pueden agregar mejoras como autenticación, almacenamiento de mensajes en una base de datos y soporte para múltiples salas de chat.


