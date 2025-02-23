import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Obtener el token desde las variables de entorno
TOKEN = os.environ.get("TOKEN")
if TOKEN is None:
    raise ValueError("El TOKEN no está configurado en las variables de entorno.")

# Configurar el bot de Telegram con Application
app = Application.builder().token(TOKEN).build()

# Definir funciones de manejo de mensajes
async def start(update: Update, context):
    await update.message.reply_text("¡Hola! Envíame un enlace de Telegram y te ayudaré a descargar el video.")

async def handle_message(update: Update, context):
    text = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {text}")

# Agregar manejadores de comandos y mensajes
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Configurar el webhook
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    print(data)  # Esto imprimirá los datos en los logs
    update = Update.de_json(data, app.bot)
    app.update_queue.put(update)
    return "ok"

@flask_app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando correctamente"


# Configurar el webhook en Telegram
async def set_webhook():
    webhook_url = f"https://tu-dominio.com/{TOKEN}"  # ← REEMPLAZA esto con la URL correcta de tu Railway
    await app.bot.set_webhook(webhook_url)

# Iniciar el servidor Flask y la aplicación de Telegram
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())  # ← Asegura que el webhook se configure antes de iniciar
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
