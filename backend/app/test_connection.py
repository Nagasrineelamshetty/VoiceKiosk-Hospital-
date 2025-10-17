# test_connection.py
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

async def test():
    client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        dbs = await client.list_database_names()
        print("✅ Connected to MongoDB Atlas!")
        print("Databases:", dbs)
    except Exception as e:
        print("❌ Connection failed:", e)

asyncio.run(test())
