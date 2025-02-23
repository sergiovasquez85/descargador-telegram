import os
import requests
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# 1. Obtener el token desde las variables de entorno
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("El TOKEN no está configurado en las variables de entorno.")

# 2. Configurar el bot de Telegram (usando la versión asíncrona)
telegram_app = Application.builder().token(TOKEN).build()

# 3. Definir funciones de manejo de mensajes
async def start(update: Update, context):
    await update.message.reply_text("¡Hola! Envíame un enlace de Telegram y te ayudaré a descargar el video.")

async def handle_message(update: Update, context):
    text = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {text}")

# Agregar los manejadores de comandos y mensajes
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 4. Configurar Flask
flask_app = Flask(__name__)

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data:
        # Convertir los datos JSON a una actualización de Telegram
        update = Update.de_json(data, telegram_app.bot)
        # Crear un nuevo event loop para procesar la actualización
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(telegram_app.process_update(update))
        loop.close()
    return "ok", 200

@flask_app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando correctamente"

# 5. Función para configurar el webhook en Telegram
def set_webhook():
    # Reemplaza 'your-railway-url.up.railway.app' por la URL real que Railway asigna a tu proyecto
    WEBHOOK_URL = f"https://your-railway-url.up.railway.app/{TOKEN}"
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        json={"url": WEBHOOK_URL}
    )
    print("Set Webhook Response:", response.json())

# 6. Iniciar la aplicación
if __name__ == "__main__":
    # Configura el webhook antes de iniciar el servidor Flask
    set_webhook()
    PORT = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=PORT)
