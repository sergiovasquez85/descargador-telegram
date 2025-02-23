import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Obtener el token desde las variables de entorno
TOKEN = os.environ.get("TOKEN")
if TOKEN is None:
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

# Configurar el webhook
flask_app = Flask(__name__)

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data:
        update = Update.de_json(data, telegram_app.bot)  # ← Posible error aquí si bot aún no está disponible
        telegram_app.update_queue.put(update)  # Enviar la actualización a la cola de procesamiento
    return "ok"

@flask_app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando correctamente"

# Configurar el webhook en Telegram
async def set_webhook():
    webhook_url = f"https://tu-dominio.com/{TOKEN}"  # ← REEMPLAZA con la URL real de tu servidor en Railway
    await telegram_app.bot.set_webhook(webhook_url)

# Iniciar el servidor Flask y la aplicación de Telegram
if __name__ == "__main__":
    import asyncio
    loop = asyncio.run(set_webhook())
    loop.run_until_complete(set_webhook()) # ← Asegura que el webhook se configure antes de iniciar
    telegram_app.run_polling()  # ← Esto mantiene el bot activo en segundo plano
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
