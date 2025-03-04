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

# Variable global para almacenar el último enlace de descarga
ultimo_download_url = None

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
    print(update.to_dict())  # Depuración
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"El file_id del video es: {file_id}")
    elif update.message.document:
        file_id = update.message.document.file_id
        await update.message.reply_text(f"El file_id del documento es: {file_id}")
    else:
        await update.message.reply_text("No se encontró video ni documento en el mensaje.")

async def handle_video(update: Update, context):
    global ultimo_download_url
    # Verifica si el mensaje tiene video o documento
    if update.message.video:
        file_id = update.message.video.file_id
    elif update.message.document:
        file_id = update.message.document.file_id
    else:
        await update.message.reply_text("No se encontró video ni documento en el mensaje.")
        return

    await update.message.reply_text(f"El file_id es: {file_id}")
    
    # Obtener el objeto File mediante get_file
    file = await context.bot.get_file(file_id)
    file_path = file.file_path  # Esto es lo que devuelve Telegram
    
    # Formar la URL de descarga y almacenarla en la variable global
    ultimo_download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    
    # Enviar la URL al usuario
    await update.message.reply_text(f"El enlace de descarga es: {ultimo_download_url}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
telegram_app.add_handler(MessageHandler(filters.VIDEO, handle_video))
telegram_app.add_handler(MessageHandler(filters.Document.ALL, handle_video))

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

# Endpoint para obtener el último enlace generado
@flask_app.route("/ultimo_enlace", methods=["GET"])
def ultimo_enlace():
    if ultimo_download_url:
        return {"success": True, "download_url": ultimo_download_url}, 200
    else:
        return {"success": False, "error": "No hay enlace disponible"}, 404

# (Opcional) Endpoint para procesar descargas
@flask_app.route("/descargar", methods=["POST"])
def descargar_video():
    data = request.get_json()
    video_url = data.get("url")
    if not video_url:
        return {"success": False, "error": "No se proporcionó URL"}, 400
    # Aquí implementarías la lógica para descargar el video.
    # Por ahora, simulamos una respuesta exitosa:
    download_url = "https://api.telegram.org/file/bot{TOKEN}/{file_path}"
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
