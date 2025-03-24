from flask import Blueprint, request, jsonify, Response
import pandas as pd
from threading import Thread
import yaml
import json
from backend.models.job import create_job, get_all_jobs, get_job_by_id
from bson import ObjectId
from datetime import datetime
from ..models.job import jobs_collection, db
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from generate_synthetic_data import generate_synthetic_data

# Creiamo un Blueprint per le API relative ai job
job_api = Blueprint('job_api', __name__)

# Funzione per serializzare ObjectId e datetime
def json_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)  # Converte ObjectId in stringa
    if isinstance(obj, datetime):
        return obj.isoformat()  # Converte datetime in formato stringa ISO 8601
    raise TypeError(f"Type {type(obj)} non serializable")

# 📌 API per creare un nuovo job
@job_api.route('/jobs', methods=['POST'])
def create_new_job():
    # Carica il file YAML di configurazione
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "File YAML mancante"}), 400

    try:
        config = yaml.safe_load(file)
    except yaml.YAMLError as e:
        return jsonify({"error": f"Errore nel caricamento del file YAML: {e}"}), 400
    
    # Creiamo un nuovo job usando i dati del file YAML
    job = create_job(config)
    
    # Serializza correttamente gli ObjectId
    job = json.loads(json.dumps(job, default=json_serializer))
    
    return jsonify({"message": "Job creato con successo", "job": job}), 201

# 📌 API per visualizzare tutti i job
@job_api.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = get_all_jobs()
    
    # Serializza correttamente gli ObjectId per ogni job
    jobs = [json.loads(json.dumps(job, default=json_serializer)) for job in jobs]
    
    return jsonify(jobs)

# 📌 API per visualizzare lo stato di un job
@job_api.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    job = get_job_by_id(job_id)
    if not job:
        return jsonify({"error": "Job non trovato"}), 404
    
    # Serializza correttamente l'ObjectId per il job
    job = json.loads(json.dumps(job, default=json_serializer))
    
    return jsonify(job)

def run_job_in_background(job_id):
    """Esegue il job in un thread separato"""
    try:
        job = get_job_by_id(job_id)
        if not job:
            print(f"❌ Job {job_id} non trovato!")
            return
        
        # Aggiorna lo stato a "Running"
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"status": "Running"}})

        # Recupera la configurazione del job
        config = job.get("config", {}).get("config", {})
        data_gen = config.get("data_generation", {})
        parameters = data_gen.get("parameters", {})
        model_name = parameters.get("model")
        num_samples = parameters.get("num_samples")

        if not model_name or not num_samples:
            raise KeyError("model o num_samples mancante")

        print(f"🚀 Avvio generazione dati per {job_id} - Modello: {model_name}, Campioni: {num_samples}")
        
        # Genera i dati
        generated_data = generate_synthetic_data(model_name, config, num_samples, job_id)

        # Salva i dati nel database
        save_synthetic_data(generated_data, job_id)

        # Aggiorna lo stato a "Completed"
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"status": "Completed"}})
        print(f"✅ Job {job_id} completato con successo!")

    except Exception as e:
        print(f"❌ Errore durante l'esecuzione del job {job_id}: {e}")
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"status": "Error", "error_message": str(e)}})

@job_api.route('/jobs/<job_id>/start', methods=['POST'])
def start_job(job_id):
    """Avvia il job in background e risponde subito con 202"""
    job = get_job_by_id(job_id)
    if not job:
        return jsonify({"error": "Job non trovato"}), 404

    # Avvia il job in un thread separato
    thread = Thread(target=run_job_in_background, args=(job_id,))
    thread.start()

    return jsonify({"message": "Job avviato in background", "job_id": job_id}), 202

# 📌 Funzione per salvare i dati sintetici nel database
def save_synthetic_data(generated_data, job_id):
    # Converte i dati sintetici in formato JSON per inserirli nel database
    sensor_data_collection = db["sensor_data"]
    data_to_insert = generated_data.to_dict(orient='records')  # Converte il DataFrame in una lista di dizionari
    # Aggiungi il job_id a ogni record generato
    for record in data_to_insert:
        record["job_id"] = job_id  # Associa il dato al job
    sensor_data_collection.insert_many(data_to_insert)  # Inserisce i dati nel database

# 📌 API per scaricare i sensori di un job
@job_api.route('/jobs/<job_id>/export', methods=['GET'])
def export_job_data(job_id):
    job = get_job_by_id(job_id)
    if not job:
        return jsonify({"error": "Job non trovato"}), 404
    
    # Recupera i dati generati per questo job
    sensor_data_collection = db["sensor_data"]
    sensor_data = list(sensor_data_collection.find({"job_id": str(job_id)}, {"_id": 0}))  # Forza conversione in stringa

    if not sensor_data:
        return jsonify({"error": "Nessun dato trovato per questo job"}), 404

    # Converti in DataFrame e genera il CSV
    df = pd.DataFrame(sensor_data)
    
    # Assicuriamoci che ci siano dati nel DataFrame
    if df.empty:
        return jsonify({"error": "Il dataset è vuoto"}), 404

    csv_data = df.to_csv(index=False)

    response = Response(csv_data, content_type="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f"attachment; filename=job_{job_id}_data.csv"
    
    return response
