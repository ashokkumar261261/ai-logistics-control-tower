import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, timedelta

# --- CONFIGURATION ---
PROJECT_ID = "inspiring-keel-423204-c7"
DATASET_ID = "logistics_control_tower"
SERVICE_ACCOUNT_FILE = "service-account.json"

def update_data():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Error: {SERVICE_ACCOUNT_FILE} not found.")
        return

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
    dataset_ref = client.dataset(DATASET_ID)

    # 1. Enhanced Shipments Data
    shipments_data = [
        {"id": 10, "origin": "London", "destination": "Paris", "status": "In Transit", "priority": "High", "cost": 1200.50, "revenue": 1800.00, "weight_kg": 500.5, "cargo_type": "Electronics", "customer_name": "Tech Corp", "delivery_date": datetime.now() + timedelta(days=1), "insurance_status": True},
        {"id": 11, "origin": "London", "destination": "Berlin", "status": "In Transit", "priority": "Standard", "cost": 1100.00, "revenue": 1600.00, "weight_kg": 800.0, "cargo_type": "Apparel", "customer_name": "Nordic Style", "delivery_date": datetime.now() + timedelta(days=2), "insurance_status": True},
        {"id": 14, "origin": "Wrightview", "destination": "New Donport", "status": "Delayed", "priority": "Standard", "cost": 850.00, "revenue": 1200.00, "weight_kg": 1200.0, "cargo_type": "Furniture", "customer_name": "Home Furnishings", "delivery_date": datetime.now() + timedelta(days=3), "insurance_status": False},
        {"id": 22, "origin": "Delhi", "destination": "Mumbai", "status": "Delivered", "priority": "Urgent", "cost": 3400.00, "revenue": 5000.00, "weight_kg": 2500.0, "cargo_type": "Medical Supplies", "customer_name": "Health Plus", "delivery_date": datetime.now() - timedelta(days=1), "insurance_status": True},
        {"id": 35, "origin": "New York", "destination": "Chicago", "status": "Pending", "priority": "High", "cost": 950.00, "revenue": 1500.00, "weight_kg": 800.0, "cargo_type": "Textiles", "customer_name": "Fashion Hub", "delivery_date": datetime.now() + timedelta(days=2), "insurance_status": True},
        {"id": 42, "origin": "Berlin", "destination": "Madrid", "status": "In Transit", "priority": "Standard", "cost": 1500.00, "revenue": 2200.00, "weight_kg": 1500.0, "cargo_type": "Machinery", "customer_name": "Auto Parts Ltd", "delivery_date": datetime.now() + timedelta(days=4), "insurance_status": True},
        {"id": 50, "origin": "Tokyo", "destination": "Seoul", "status": "Delayed", "priority": "High", "cost": 2100.00, "revenue": 3200.00, "weight_kg": 600.0, "cargo_type": "Robotics", "customer_name": "Future Automation", "delivery_date": datetime.now() + timedelta(days=1), "insurance_status": True}
    ]
    df_shipments = pd.DataFrame(shipments_data)

    # 2. Enhanced Drivers Data
    drivers_data = [
        {"id": 1, "name": "Kyle Miller", "license_number": "TX-9988", "status": "On Duty", "rating": 4.8, "experience_years": 10, "current_location": "London", "contact_number": "+1-555-0101", "salary": 4500.00},
        {"id": 2, "name": "Sarah Jenkins", "license_number": "CA-4422", "status": "Off Duty", "rating": 4.9, "experience_years": 5, "current_location": "Paris", "contact_number": "+1-555-0102", "salary": 3800.00},
        {"id": 3, "name": "John Doe", "license_number": "NY-1122", "status": "On Duty", "rating": 4.5, "experience_years": 12, "current_location": "New York", "contact_number": "+1-555-0103", "salary": 5000.00},
        {"id": 4, "name": "Emma Wilson", "license_number": "IL-3344", "status": "Maintenance", "rating": 4.7, "experience_years": 7, "current_location": "Chicago", "contact_number": "+1-555-0104", "salary": 4200.00},
        {"id": 5, "name": "Raj Patel", "license_number": "MH-0011", "status": "On Duty", "rating": 4.6, "experience_years": 15, "current_location": "Mumbai", "contact_number": "+91-9988-7766", "salary": 5500.00}
    ]
    df_drivers = pd.DataFrame(drivers_data)

    # 3. Enhanced Vehicles Data
    vehicles_data = [
        {"vehicle_id": 1, "type": "Heavy Truck", "capacity_kg": 15000, "status": "Active", "fuel_level": 75.5, "last_service_date": "2023-10-01", "mileage_km": 120000.5, "current_load_kg": 5000.0, "gps_coordinates": "51.5074 N, 0.1278 W"},
        {"vehicle_id": 2, "type": "Medium Truck", "capacity_kg": 8000, "status": "Active", "fuel_level": 45.0, "last_service_date": "2023-11-15", "mileage_km": 85000.0, "current_load_kg": 6000.0, "gps_coordinates": "48.8566 N, 2.3522 E"},
        {"vehicle_id": 3, "type": "Heavy Truck", "capacity_kg": 18000, "status": "Active", "fuel_level": 90.0, "last_service_date": "2023-09-20", "mileage_km": 150000.0, "current_load_kg": 15000.0, "gps_coordinates": "35.6762 N, 139.6503 E"},
        {"vehicle_id": 4, "type": "Light Van", "capacity_kg": 2500, "status": "Maintenance", "fuel_level": 10.5, "last_service_date": "2023-12-20", "mileage_km": 45000.2, "current_load_kg": 0.0, "gps_coordinates": "40.7128 N, 74.0060 W"}
    ]
    df_vehicles = pd.DataFrame(vehicles_data)

    datasets = {
        "shipments": df_shipments,
        "drivers": df_drivers,
        "vehicles": df_vehicles
    }

    for table_name, df in datasets.items():
        print(f"Updating {table_name}...")
        table_ref = dataset_ref.table(table_name)
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        client.load_table_from_dataframe(df, table_ref, job_config=job_config).result()
        print(f"Successfully updated {table_name}.")

if __name__ == "__main__":
    update_data()
