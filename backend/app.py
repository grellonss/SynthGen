from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from threading import Thread
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.api.job_api import run_job_in_background
from backend.models.sensor_data import insert_sensor_data, get_all_sensor_data
from backend.api import job_api as job_api_module

# Inizializziamo Flask
app = Flask(__name__)
CORS(app, origins="http://localhost:3000")
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", async_mode="threading")

# Passa l'istanza di socketio a job_api
job_api_module.set_socketio(socketio)
job_api = job_api_module.job_api  # Recupera il Blueprint

# 📌 API per l'evento in seguito allo start del bottone
@socketio.on('start_job')
def handle_start_job(data):
    job_id = data.get('job_id')
    if not job_id:
        print("⚠️ job_id mancante nell'evento start_job")
        return

    print(f"📡 Ricevuto evento WebSocket 'start_job' per il job {job_id}")
    
    # Avvia il job in un thread separato (riutilizzi la tua funzione)
    thread = Thread(target=run_job_in_background, args=(job_id,))
    thread.start()

# Connessione a MongoDB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["cps_database"]

# 📌 Creiamo un Blueprint per i sensori
sensor_api = Blueprint("sensor_api", __name__)

# 📌 API per ottenere tutti i dati
@sensor_api.route("/sensors", methods=["GET"])
def get_sensors():
    sensors = get_all_sensor_data()
    return jsonify(sensors)

# 📌 API per inserire un nuovo sensore
@sensor_api.route("/sensors", methods=["POST"])
def add_sensor():
    data = request.json

    if not all(k in data for k in ["id_macchina", "valore", "nome_parametro", "tipo_dato"]):
        return jsonify({"error": "Dati mancanti"}), 400

    new_sensor = insert_sensor_data(data["id_macchina"], data["valore"], data["nome_parametro"], data["tipo_dato"])
    return jsonify({"message": "Dati inseriti con successo!", "data": new_sensor}), 201

# 📌 API per ricevere dati sintetici e salvarli nel DB
@sensor_api.route("/sensors/upload", methods=["POST"])
def upload_synthetic_data():
    data = request.json  # Riceve i dati in formato JSON
    
    if not data:
        return jsonify({"error": "Nessun dato ricevuto"}), 400

    try:
        # Se i dati sono in lista, inseriscili tutti, altrimenti un solo record
        if isinstance(data, list):
            db["sensor_data"].insert_many(data)
        else:
            db["sensor_data"].insert_one(data)

        return jsonify({"message": "Dati sintetici caricati con successo!"}), 201
    except Exception as e:
        return jsonify({"error": f"Errore nell'inserimento dei dati: {str(e)}"}), 500


# 📌 Registriamo i Blueprint
app.register_blueprint(job_api, url_prefix="/api")
app.register_blueprint(sensor_api, url_prefix="/api")  # Ora i sensori saranno sotto /api/

# 📌 Avvio del server Flask sulla porta 5000
if __name__ == "__main__":
    print("✅ Avviando il server Flask con SocketIO...")
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
