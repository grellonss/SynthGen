import uuid
import datetime
from pymongo import MongoClient

# Connessione a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["cps_database"]
jobs_collection = db["jobs"]

# Funzione per creare un nuovo job
def create_job(config):
    # Genera un ID unico per il job
    job_id = str(uuid.uuid4())
    
    # Prepara i dati del job
    job_data = {
        "job_id": job_id,
        "config": config,  # Configurazione YAML del job
        "status": "Inizializzato",  # Stato iniziale
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }
    
    # Inserisce il job nel database
    jobs_collection.insert_one(job_data)
    
    return job_data

# Funzione per ottenere tutti i job
def get_all_jobs():
    jobs = list(jobs_collection.find())  # Trova tutti i job
    for job in jobs:
        job["_id"] = str(job["_id"])  # Converte ObjectId in stringa
    return jobs

# Funzione per ottenere un job per ID
def get_job_by_id(job_id):
    job = jobs_collection.find_one({"job_id": job_id})
    if job:
        job["_id"] = str(job["_id"])  # Converte ObjectId in stringa
    return job
