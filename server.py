import os
import requests
import threading
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
    """Recibe las actualizaciones de Telegram y las pasa a la app de Telegram"""
    data = request.get_json()
    if data:
        update = Update.de_json(data, telegram_app.bot)
        telegram_app.create_task(telegram_app.process_update(update))
    return "ok", 200

@flask_app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando correctamente"

# Configurar Webhook en Telegram
def set_webhook():
    WEBHOOK_URL = f"https://descargador-telegram-production.up.railway.app/{TOKEN}"  # Reemplaza con tu URL real
    try:
        response = requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", json={"url": WEBHOOK_URL})
        print("Webhook configurado:", response.json())
    except Exception as e:
        print("Error al configurar el webhook:", e)

# Ejecutar el bot en segundo plano
def run_telegram_bot():
    telegram_app.run_polling()

if __name__ == "__main__":
    # Configurar el Webhook antes de iniciar Flask
    set_webhook()

    # Iniciar el bot en un hilo separado para que no bloquee Flask
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Iniciar el servidor Flask
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
