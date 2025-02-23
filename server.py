import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Obtener el token desde las variables de entorno
TOKEN = os.environ.get("TOKEN")
if TOKEN is None:
    raise ValueError("El TOKEN no está configurado en las variables de entorno.")

# Configurar el bot de Telegram con Application
app = Application.builder().token(TOKEN).build()

# Definir funciones de manejo de mensajes
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("¡Hola! Envíame un enlace de Telegram y te ayudaré a descargar el video.")

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {text}")

# Agregar manejadores de comandos y mensajes
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Configurar el webhook
flask_app = Flask(__name__)

@flask_app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), app.bot)
    await app.update_queue.put(update)
    return "ok"

# Iniciar el servidor Flask
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
