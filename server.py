import os
import requests
import asyncio
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# 1. Obtener el token desde la variable de entorno
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

# 4. Inicializar la aplicación de Telegram en el event loop global
async def init_bot():
    await telegram_app.initialize()

future_init = asyncio.run_coroutine_threadsafe(init_bot(), bot_loop)
future_init.result()  # Espera a que la inicialización termine

# 5. Definir los handlers para Telegram
async def start(update: Update, context):
    await update.message.reply_text("¡Hola! Envíame un enlace de Telegram y te ayudaré a descargar el video.")

async def handle_message(update: Update, context):
    print(update.to_dict())  # Imprime todo el contenido del mensaje para depuración
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"El file_id del video es: {file_id}")
    elif update.message.document:
        file_id = update.message.document.file_id
        await update.message.reply_text(f"El file_id del documento es: {file_id}")
    else:
        await update.message.reply_text("No se encontró video ni documento en el mensaje.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 6. Configurar Flask
# La carpeta "static" debe estar en la raíz del proyecto y contener el archivo index.html.
flask_app = Flask(__name__, static_folder='static')

# Ruta para servir la página web (index.html)
@flask_app.route("/", methods=["GET"])
def home():
    return flask_app.send_static_file("index.html")

# Endpoint para el webhook de Telegram
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data:
        update = Update.de_json(data, telegram_app.bot)
        # Envía la actualización al event loop global sin cerrar el loop
        asyncio.run_coroutine_threadsafe(telegram_app.process_update(update), bot_loop)
    return "ok", 200

# (Opcional) Endpoint para procesar descargas
@flask_app.route("/descargar", methods=["POST"])
def descargar_video():
    data = request.get_json()
    video_url = data.get("url")
    if not video_url:
        return {"success": False, "error": "No se proporcionó URL"}, 400
    # Aquí implementarías la lógica para descargar el video.
    # Por ahora, simulamos una respuesta exitosa:
    download_url = "https://mi-cdn.com/videos/ejemplo_video.mp4"
    return {"success": True, "download_url": download_url}, 200

# 7. Función para configurar el webhook en Telegram
def set_webhook():
    # Reemplaza 'your-real-railway-url.up.railway.app' con la URL real asignada a tu servicio Railway.
    WEBHOOK_URL = f"https://descargador-telegram-production.up.railway.app/{TOKEN}"
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        json={"url": WEBHOOK_URL}
    )
    print("Set Webhook Response:", response.json())

# 8. Arranque de la aplicación
if __name__ == "__main__":
    set_webhook()  # Configura el webhook en Telegram
    PORT = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=PORT)
