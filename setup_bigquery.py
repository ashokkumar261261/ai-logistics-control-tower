import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from sqlalchemy import create_engine
import sqlite3

# --- CONFIGURATION ---
# REPLACE THESE WITH YOUR ACTUAL VALUES
PROJECT_ID = "inspiring-keel-423204-c7"
DATASET_ID = "logistics_control_tower"
SERVICE_ACCOUNT_FILE = "service-account.json"
SQLITE_DB = "sales_data.db"

def setup_bigquery():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Error: {SERVICE_ACCOUNT_FILE} not found. Please upload it to the root folder.")
        return

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

    # 1. Create Dataset
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} already exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset)
        print(f"Created dataset {DATASET_ID}")

    # 2. Migrate SQLite Tables
    conn = sqlite3.connect(SQLITE_DB)
    tables = ["shipments", "drivers", "vehicles"]
    
    for table in tables:
        print(f"Migrating {table}...")
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        
        # Load into BigQuery
        table_ref = dataset_ref.table(table)
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        client.load_table_from_dataframe(df, table_ref, job_config=job_config).result()
        print(f"Successfully migrated {table} to BigQuery.")

    # 3. Setup Gemini Model in BigQuery (BigQuery ML)
    # Note: This requires the 'Vertex AI User' role on the service account.
    print("Setting up BigQuery ML (Gemini)...")
    connection_id = f"{PROJECT_ID}.us.vertex-ai-conn"
    
    # This part often requires manual connection creation in the console, 
    # but we can try to create the remote model if the connection exists.
    model_sql = f"""
    CREATE OR REPLACE MODEL `{PROJECT_ID}.{DATASET_ID}.gemini_model`
    REMOTE WITH CONNECTION `{connection_id}`
    OPTIONS(ENDPOINT = 'gemini-1.5-flash');
    """
    try:
        client.query(model_sql).result()
        print("BigQuery ML Gemini model configured.")
    except Exception as e:
        print(f"Warning: Could not create ML model automatically. You may need to create the connection manually. Error: {e}")

if __name__ == "__main__":
    setup_bigquery()
