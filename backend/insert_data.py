import os
import sys
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# --- Ensure the app package is discoverable ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

# --- Import MongoDB connection ---
from db import db  # Make sure db.py uses pymongo.MongoClient, not motor

# --- CSV file mappings ---
collections = {
    "departments": "data/departments.csv",
    "doctors": "data/doctors.csv",
    "services": "data/services.csv",
    "visiting_hours": "data/visiting_hours.csv",
    "emergency_contacts": "data/emergency_contacts.csv",
    "faqs": "data/faqs.csv",
}

def insert_csv_data():
    for collection_name, csv_path in collections.items():
        try:
            print(f"\n📄 Processing '{collection_name}' from: {csv_path}")
            
            # Check if file exists
            if not os.path.exists(csv_path):
                print(f"❌ File not found: {csv_path}")
                continue

            # Read CSV
            df = pd.read_csv(csv_path)
            print(f"✅ Columns found: {df.columns.tolist()}, Rows: {len(df)}")
            
            if df.empty:
                print(f"⚠️ CSV is empty: {csv_path}")
                continue

            # Drop _id column if present
            if "_id" in df.columns:
                df = df.drop(columns=["_id"])

            # Convert to list of dicts
            data = df.to_dict(orient="records")

            if not data:
                print(f"⚠️ No valid data to insert for {collection_name}")
                continue

            # Insert into MongoDB
            try:
                result = db[collection_name].insert_many(data, ordered=False)
                inserted_count = len(result.inserted_ids) if hasattr(result, "inserted_ids") else 0
                print(f"✅ Inserted {inserted_count} records into '{collection_name}' collection.")
            except BulkWriteError as bwe:
                print(f"⚠️ Duplicate or insertion error in '{collection_name}': {bwe.details}")

        except Exception as e:
            print(f"❌ Error processing '{collection_name}': {e}")

if __name__ == "__main__":
    print("🚀 Starting CSV to MongoDB import...")
    insert_csv_data()
    print("\n✅ Data import completed.")
