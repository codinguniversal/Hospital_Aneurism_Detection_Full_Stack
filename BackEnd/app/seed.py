import random
import uuid
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from faker import Faker

# We can leverage your global config to avoid hardcoding database strings
from app.config import settings
# Assuming you have a password hashing function in your security module
from app.services.security import get_password_hash  

fake = Faker()

# Connect to MongoDB server using your configurations
client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_db_name]

# Define collections
patients_collection = db["patients"]
users_collection = db["users"]

scan_paths = [
    "E:/for database/Have Ane/1.zip",
    "E:/for database/Have Ane/5.zip",
    "E:/for database/normal/1.zip",
    "E:/for database/normal/2.zip"
]

def setup_database_constraints():
    """Establishes unique identifier constraints on the database collections."""
    print("Enforcing unique constraint database indexes...")
    # Ensures no duplicate emails or employee IDs can ever be inserted
    users_collection.create_index([("email", ASCENDING)], unique=True)
    users_collection.create_index([("employeeId", ASCENDING)], unique=True)

def seed_admin_user():
    """Seeds a primary administrator record into the users collection."""
    print("Seeding admin user record...")
    
    admin_email = "admin@hospital.com"
    admin_payload = {
        "employeeId": "EMP-ADMIN-01",
        "email": admin_email,
        # Securely hash the seed password matching your backend authentication logic
        "password": get_password_hash("SuperSecretAdmin2026!"),
        "role": "admin"
    }
    
    # Using update_one with upsert=True prevents duplicate crashes if seed is run multiple times
    users_collection.update_one(
        {"email": admin_email},
        {"$set": admin_payload},
        upsert=True
    )
    print("Admin user seeded successfully.")

def generate_bulk_patient_data(num_records=5):
    """Generates bulk dummy patient cases for development simulation testing."""
    print(f"Generating {num_records} dummy patient records...")
    seeded_documents = []
    
    for _ in range(num_records):
        patient_id = f"PT-{random.randint(10000, 99999)}"
        scan_id = f"SCN-2026-{str(uuid.uuid4())[:8]}"
        
        doc = {
            "_id": patient_id,
            "patient_name": fake.name(),
            "birth_date": fake.date_of_birth(minimum_age=25, maximum_age=75).strftime("%Y-%m-%d"),
            "assigned_doc": random.choice(["dr_smith", "dr_neurologist_1"]),
            "medical_history": [fake.sentence() for _ in range(random.randint(1, 3))],
            "scans": [
                {
                    "id": scan_id,
                    "scan_date": datetime.utcnow(),
                    "status": "Pending",
                    "img_file_path": random.choice(scan_paths),
                    "results": {}
                }
            ]
        }
        seeded_documents.append(doc)
        
    patients_collection.insert_many(seeded_documents)
    print(f"Successfully seeded {num_records} dynamic patient documents into patients collection!")

if __name__ == "__main__":
    # 1. Force safety indexes
    setup_database_constraints()
    
    # 2. Seed administrative auth access
    seed_admin_user()
    
    # 3. Build dummy clinical records
    generate_bulk_patient_data(5)