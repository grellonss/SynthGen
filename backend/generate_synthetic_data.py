import pymongo
import pandas as pd
from sdv.tabular import GaussianCopula

# Connessione a MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["cps_database"]  # Nome del database
collection = db["sensor_data"]  # Nome della collezione

def generate_synthetic_data(model_name, config, num_samples):
    # Estrai i dati reali dal database (o usa una collezione di riferimento)
    data = list(collection.find({}, {"_id": 0}))  # Non includere "_id" nei dati per SDV
    df = pd.DataFrame(data)

    # Seleziona il modello di generazione dei dati
    if model_name == "CTGAN":
        model = GaussianCopula()  # Usa il modellA"""  """o di generazione dati di SDV (ad esempio CTGAN)
    else:
        raise ValueError(f"Model '{model_name}' non supportato")
    
    # Addestra il modello sui dati reali
    model.fit(df)

    # Genera i dati sintetici""" AA """A"""  """
    synthetic_data = model.sample(num_samples)

    # Restituisci i dati generati
    return synthetic_data
