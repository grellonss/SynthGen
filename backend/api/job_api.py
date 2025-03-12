from flask import Blueprint, request, jsonify
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
    raise TypeError(f"Type {type(obj)} not serializable")

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
    
    # Serializza correttamente gli ObjectId (usando la funzione json_serializer)
    job = json.loads(json.dumps(job, default=json_serializer))  # Usa json_serializer per serializzare
    
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

# 📌 API per avviare l'esecuzione di un job
@job_api.route('/jobs/<job_id>/start', methods=['POST'])
def start_job(job_id):
    job = get_job_by_id(job_id)  # Ottieni il job tramite l'id
    if not job:
        return jsonify({"error": "Job non trovato"}), 404
    
    # Cambia lo stato del job in "In esecuzione"
    jobs_collection.update_one({"job_id": job_id}, {"$set": {"status": "In esecuzione"}})

    # Recupera la configurazione del job
    config = job['config']

    try:
        model_name = config['model']  # Es. "CTGAN"
        num_samples = config['num_samples']

        # Chiamata alla funzione di generazione dei dati sintetici
        generated_data = generate_synthetic_data(model_name, config, num_samples)  # La funzione restituisce un DataFrame

        # Salva i dati generati nella collezione sensor_data
        save_synthetic_data(generated_data)

        # Esegui l'aggiornamento dello stato del job a "Completato"
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"status": "Completato"}})
        return jsonify({"message": "Job avviato con successo", "job": job}), 200
    except Exception as e:
        # Gestione degli errori
        jobs_collection.update_one({"job_id": job_id}, {"$set": {"status": "Errore", "error_message": str(e)}})
        return jsonify({"error": f"Errore durante l'esecuzione del job: {e}"}), 500

# Funzione per salvare i dati sintetici nel database
def save_synthetic_data(generated_data):
    # Converte i dati sintetici in formato JSON per inserirli nel database
    # Se `generated_data` è un DataFrame, lo convertiamo in un dizionario
    sensor_data_collection = db["sensor_data"]
    data_to_insert = generated_data.to_dict(orient='records')  # Converte il DataFrame in una lista di dizionari
    sensor_data_collection.insert_many(data_to_insert)  # Inserisce i dati nel database