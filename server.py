import os
import requests
import asyncio
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# 1. Obtener el token desde las variables de entorno
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("El TOKEN no está configurado en las variables de entorno.")

# 2. Crear la aplicación de Telegram
telegram_app = Application.builder().token(TOKEN).build()

# 3. Crear un event loop global para el bot y ejecutarlo en un hilo separado
bot_loop = asyncio.new_event_loop()

def start_bot_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

bot_thread = threading.Thread(target=start_bot_loop, args=(bot_loop,), daemon=True)
bot_thread.start()

# 4. Inicializar la aplicación de Telegram en el loop global
async def init_bot():
    await telegram_app.initialize()

# Programar la inicialización y esperar a que se complete
future_init = asyncio.run_coroutine_threadsafe(init_bot(), bot_loop)
future_init.result()  # Bloquea hasta que se complete la inicialización

# 5. Definir funciones de manejo de mensajes
async def start(update: Update, context):
    await update.message.reply_text("¡Hola! Envíame un enlace de Telegram y te ayudaré a descargar el video.")

async def handle_message(update: Update, context):
    text = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {text}")

# 6. Agregar los manejadores a la aplicación de Telegram
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 7. Configurar Flask
flask_app = Flask(__name__)

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data:
        update = Update.de_json(data, telegram_app.bot)
        # Enviar la tarea al loop global sin cerrarlo
        asyncio.run_coroutine_threadsafe(telegram_app.process_update(update), bot_loop)
    return "ok", 200

@flask_app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando correctamente"

# 8. Función para configurar el webhook en Telegram
def set_webhook():
    # Reemplaza 'your-real-railway-url.up.railway.app' con la URL real asignada a tu servicio Railway
    WEBHOOK_URL = f"https://descargador-telegram-production.up.railway.app/{TOKEN}"
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        json={"url": WEBHOOK_URL}
    )
    print("Set Webhook Response:", response.json())

# 9. Arranque de la aplicación
if __name__ == "__main__":
    set_webhook()  # Configura el webhook en Telegram
    PORT = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=PORT)
