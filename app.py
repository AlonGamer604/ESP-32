import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# URI desde variable de entorno (seguridad)
MONGO_URI = os.environ.get("MONGO_URI")

# Cliente MongoDB con timeout corto para evitar cuelgues
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["ESP-32"]
collection = db["Datos"]

# Ruta para recibir datos del ESP32
@app.route("/api/data", methods=["POST"])
def recibir_dato():
    data = request.get_json()
    required_keys = ["dispositivo", "temperatura", "humedad"]
    if not all(k in data for k in required_keys):
        return jsonify({"error": "Faltan campos en el JSON"}), 400

    documento = {
        "dispositivo": data["dispositivo"],
        "temperatura": data["temperatura"],
        "humedad": data["humedad"],
        "timestamp": datetime.utcnow() - timedelta(hours=6)
    }

    try:
        collection.insert_one(documento)
        return jsonify({"message": "Datos guardados correctamente"}), 200
    except Exception as e:
        print("Error al insertar en MongoDB:", e)
        return jsonify({"error": "Error al guardar los datos"}), 500

# Ruta para ver los últimos 50 datos
@app.route("/api/datos", methods=["GET"])
def ver_datos():
    try:
        datos = list(collection.find().sort("timestamp", -1).limit(50))
        for d in datos:
            d["_id"] = str(d["_id"])
            d["timestamp"] = d["timestamp"].isoformat()
        return jsonify(datos), 200
    except Exception as e:
        print("Error al leer de MongoDB:", e)
        return jsonify({"error": "Error al obtener los datos"}), 500

# Ruta raíz
@app.route("/", methods=["GET"])
def index():
    return "API Flask con MongoDB funcionando en Render", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

