import os
import time
import requests
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", 60))

if not MONGO_URI:
    raise EnvironmentError("MONGO_URI not set in .env")

client = MongoClient(MONGO_URI)
db = client["financial_data"]
collection = db["forex_prices"]

def fetch_forex_rates(base="USD"):
    url = f"https://api.frankfurter.app/latest?from={base}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    print("API response:", data)
    return data

def store_rates(data):
    if "rates" not in data or not data["rates"]:
        print("Invalid data, skipping insert.")
        return

    doc = {
        "timestamp": datetime.utcnow().isoformat(),
        "base": data.get("base", ""),
        "rates": data["rates"],
        "date": data.get("date", "")
    }
    collection.insert_one(doc)
    print(f"Inserted forex data for {doc['timestamp']}")

def main():
    while True:
        try:
            data = fetch_forex_rates()
            store_rates(data)
        except Exception as e:
            print(f"Error fetching or storing forex data: {e}")
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
