from flask import Flask, request, jsonify
from pymongo import MongoClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.sensor_data import insert_sensor_data, get_all_sensor_data
from backend.api.job_api import job_api

import sys
print("Current PYTHONPATH:", sys.path)


# Inizializziamo Flask
app = Flask(__name__)

# Registriamo il blueprint
app.register_blueprint(job_api, url_prefix="/api")


# 📌 API per ottenere tutti i dati
@app.route("/sensors", methods=["GET"])
def get_sensors():
    sensors = get_all_sensor_data()
    return jsonify(sensors)


# 📌 API per inserire un nuovo sensore (POST)
@app.route("/sensors", methods=["POST"])
def add_sensor():
    data = request.json

    if not all(k in data for k in ["id_macchina", "valore", "nome_parametro", "tipo_dato"]):
        return jsonify({"error": "Dati mancanti"}), 400

    new_sensor = insert_sensor_data(data["id_macchina"], data["valore"], data["nome_parametro"], data["tipo_dato"])
    return jsonify({"message": "Dati inseriti con successo!", "data": new_sensor}), 201



# 📌 Avvio del server Flask sulla porta 5001
if __name__ == "__main__":
    print("✅ Avviando il server Flask...")
    app.run(debug=True, host="127.0.0.1", port=5000)

