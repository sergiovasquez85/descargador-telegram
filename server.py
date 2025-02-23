import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Obtener el token desde las variables de entorno
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("El TOKEN no está configurado en las variables de entorno.")

# Configurar el bot de Telegram con Application
telegram_app = Application.builder().token(TOKEN).build()

# Definir funciones de manejo de mensajes
async def start(update: Update, context):
    await update.message.reply_text("¡Hola! Envíame un enlace de Telegram y te ayudaré a descargar el video.")

async def handle_message(update: Update, context):
    text = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {text}")

# Agregar manejadores de comandos y mensajes
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Configurar Flask
flask_app = Flask(__name__)

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data:
        update = Update.de_json(data, telegram_app.bot)
        telegram_app.update_queue.put(update)
    return "ok", 200

@flask_app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando correctamente"

# Configurar Webhook en Telegram
def set_webhook():
    WEBHOOK_URL = f"https://tu-app.railway.app/{TOKEN}"  # Reemplaza con la URL de tu Railway
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
    print(response.json())

# Iniciar el servidor
if __name__ == "__main__":
    set_webhook()  # Configura el webhook antes de iniciar Flask
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
