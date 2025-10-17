# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "hospital_helpdesk")

# Async MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
faqs_collection = db["faqs"]
doctors_collection = db["doctors"]
departments_collection = db["departments"]
services_collection = db["services"]
visiting_hours_collection = db["visiting_hours"]
emergency_contacts_collection = db["emergency_contacts"]
