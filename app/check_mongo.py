from pymongo import MongoClient
import os

def check_mongo():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = MongoClient(mongo_url)
    db = client["users_db"]
    collection = db["engines"]
    
    print(f"Checking {db.name}.{collection.name}...")
    count = collection.count_documents({})
    print(f"Found {count} documents.")
    
    if count > 0:
        for doc in collection.find().limit(5):
            print(doc)

if __name__ == "__main__":
    check_mongo()
