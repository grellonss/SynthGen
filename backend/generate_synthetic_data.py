import pymongo
import pandas as pd
from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer
from sdv.metadata import SingleTableMetadata
from sdmetrics.reports.single_table import QualityReport

# Connessione a MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["cps_database"]
collection = db["sensor_data"]

def generate_synthetic_data(model_name, config, num_samples, job_id):
    print(f"📡 Recupero dati reali dal database per il job: {job_id}...")

    # Estrai i dati reali dal database
    data = list(collection.find({}, {"_id": 0, "id_macchina": 1, "valore": 1, "nome_parametro": 1, "tipo_dato": 1}))

    if not data:
        raise ValueError("⚠️ ERRORE: Non ci sono dati reali nel database per generare quelli sintetici!")

    df = pd.DataFrame(data)
    print(f"📊 Dataset reale caricato: {df.shape[0]} righe, {df.shape[1]} colonne.")

    # ✅ Crea i metadata in automatico
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)

    # ✅ Seleziona e inizializza il modello con metadata
    if model_name == "CTGAN":
        model = CTGANSynthesizer(metadata)
    elif model_name == "GaussianCopula":
        model = GaussianCopulaSynthesizer(metadata)
    else:
        raise ValueError(f"⚠️ ERRORE: Model '{model_name}' non supportato")

    print("🚀 Avvio addestramento del modello SDV...")
    model.fit(df)
    print("✅ Addestramento completato!")

    # Genera i dati sintetici
    print(f"🛠 Generazione di {num_samples} dati sintetici...")
    synthetic_data = model.sample(num_rows=num_samples)
    print(f"✅ Dati sintetici generati: {synthetic_data.shape[0]} righe")

    # 📈 Valutazione della qualità dei dati sintetici
    print("📈 Valutazione della qualità dei dati sintetici...")
    report = QualityReport()
    report.generate(real_data=df, synthetic_data=synthetic_data, metadata=metadata.to_dict())

    score = report.get_score()
    print(f"📊 Qualità dei dati sintetici (0-1): {score:.2f}")

    # Converti in formato JSON per MongoDB
    synthetic_data_records = synthetic_data.to_dict(orient="records")
    for record in synthetic_data_records:
        record["job_id"] = job_id

    synthetic_collection = db["sensor_data_generated"]
    synthetic_collection.insert_many(synthetic_data_records)

    print(f"✅ Dati sintetici salvati in MongoDB per il job {job_id}!")

    return synthetic_data
