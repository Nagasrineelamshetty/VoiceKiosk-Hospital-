# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "hospital_voice")

# Async MongoDB client
client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

# Collections
doctors_collection = db["doctors"]
departments_collection = db["departments"]
services_collection = db["services"]
visiting_hours_collection = db["visiting_hours"]
emergency_contacts_collection = db["emergency_contacts"]
faqs_collection = db["faqs"]

print("✅ Async MongoDB connection ready")
