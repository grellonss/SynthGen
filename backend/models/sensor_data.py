import pymongo
from bson import ObjectId
from datetime import datetime, timezone
import uuid

# Connessione al database MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["cps_database"]  # Nome del database
collection = db["sensor_data"]  # Nome della collezione


# Funzione per recuperare tutti i dati
def get_all_sensor_data():
    sensors = list(collection.find())
     # Converti _id da ObjectId a stringa per JSON
    for sensor in sensors:
        sensor["_id"] = str(sensor["_id"])
    
    return sensors



# Funzione per inserire un nuovo dato del sensore
def insert_sensor_data(id_macchina, valore, nome_parametro, tipo_dato):
    data = {
        "_id": str(uuid.uuid4()),  # Genera un UUID univoco per il record
        "id_macchina": id_macchina,
        "valore": valore,
        "data_registrazione": datetime.now(timezone.utc),
        "nome_parametro": nome_parametro,
        "tipo_dato": tipo_dato,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc)
    }
    collection.insert_one(data)

    inserted_data = collection.find_one({"_id": data["_id"]}, {"_id": 0})  
    return inserted_data
