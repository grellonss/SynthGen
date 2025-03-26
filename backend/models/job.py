import uuid
from datetime import datetime, timezone
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
        "job_id": job_id,  # Aggiungi un campo job_id unico
        "config": config,  # Configurazione YAML del job
        "status": "Initialized",  # Stato iniziale
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    # Inserisce il job nel database e ottiene l'ID MongoDB generato
    inserted_job = jobs_collection.insert_one(job_data)

    # Recupera il job appena inserito con il campo _id di MongoDB
    job_data["_id"] = str(inserted_job.inserted_id)  # Aggiungi l'_id generato

    return job_data

# Funzione per ottenere tutti i job
def get_all_jobs():
    jobs = list(jobs_collection.find())  # Trova tutti i job
    for job in jobs:
        job["_id"] = str(job["_id"])  # Converte ObjectId in stringa
        if "created_at" in job:
            job["created_at"] = job["created_at"].isoformat()
        if "started_at" in job:
            job["started_at"] = job["started_at"].isoformat()
        if "completed_at" in job:
            job["completed_at"] = job["completed_at"].isoformat()
    return jobs

# Funzione per ottenere un job per ID
def get_job_by_id(job_id):
    job = jobs_collection.find_one({"job_id": job_id})
    if job:
        job["_id"] = str(job["_id"])  # Converte ObjectId in stringa
    return job
