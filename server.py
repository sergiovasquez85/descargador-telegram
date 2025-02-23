from flask import Flask, request, jsonify, send_file
import requests
import os

app = Flask(__name__)

# Configura tu bot de Telegram
TOKEN = "TU_BOT_TOKEN"
API_URL = f"https://api.telegram.org/bot{TOKEN}/"

def obtener_file_id(url):
    """ Extraer el ID del archivo desde la URL de Telegram """
    # Aquí debes extraer el file_id desde la URL compartida
    return "FILE_ID_EXTRAIDO"

def obtener_file_path(file_id):
    """ Obtener la ruta del archivo desde Telegram """
    response = requests.get(f"{API_URL}getFile?file_id={file_id}").json()
    return response.get("result", {}).get("file_path")

@app.route("/descargar", methods=["POST"])
def descargar_video():
    data = request.json
    url = data.get("url")

    file_id = obtener_file_id(url)
    if not file_id:
        return jsonify({"success": False, "error": "No se pudo obtener el video"})

    file_path = obtener_file_path(file_id)
    if not file_path:
        return jsonify({"success": False, "error": "Error al obtener la ruta del archivo"})

    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    
    video_filename = "video.mp4"
    with open(video_filename, "wb") as f:
        f.write(requests.get(file_url).content)

    return send_file(video_filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
