import random
import uuid
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from faker import Faker

from app.config import static_settings
from BackEnd.app.infrastructure.services.security import get_password_hash  

fake = Faker()

client = MongoClient(static_settings.mongodb_uri)
db = client[static_settings.mongodb_db_name]

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
    users_collection.create_index([("email", ASCENDING)], unique=True)
    users_collection.create_index([("employeeId", ASCENDING)], unique=True)

def seed_admin_user():
    """Seeds a primary administrator record."""
    print("Seeding admin user record...")
    admin_email = "admin@hospital.com"
    admin_payload = {
        "employeeId": "EMP-ADMIN-01",
        "email": admin_email,
        "password": get_password_hash("SuperSecretAdmin2026!"),
        "role": "admin"
    }
    users_collection.update_one({"email": admin_email}, {"$set": admin_payload}, upsert=True)
    print("Admin user seeded successfully.")

def seed_doctor_users():
    print("Seeding doctor user records...")
    
    # for postman testing
    doctors = [
        {
            "employeeId": "dr_smith",
            "email": "smith@hospital.com",
            "password": get_password_hash("DoctorSmith2026!"),
            "role": "doctor"
        },
        {
            "employeeId": "dr_neurologist_1",
            "email": "neuro1@hospital.com",
            "password": get_password_hash("NeuroPassword2026!"),
            "role": "doctor"
        }
    ]
    
    for doc in doctors:
        users_collection.update_one(
            {"employeeId": doc["employeeId"]}, 
            {"$set": doc}, 
            upsert=True
        )
    print(f"Successfully seeded {len(doctors)} doctor records.")

def generate_bulk_patient_data(num_records=5):
    """Generates bulk dummy patient cases assigned to our seeded doctors."""
    print(f"Generating {num_records} dummy patient records...")
    seeded_documents = []
    
    for _ in range(num_records):
        patient_id = f"PT-{random.randint(10000, 99999)}"
        scan_id = f"SCN-2026-{str(uuid.uuid4())[:8]}"
        
        doc = {
            "_id": patient_id,
            "patient_name": fake.name(),
            "birth_date": fake.date_of_birth(minimum_age=25, maximum_age=75).strftime("%Y-%m-%d"),
            # Matches the exact doctor employeeIds we just seeded above!
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
    print(f"Successfully seeded {num_records} dynamic patient documents!")

if __name__ == "__main__":
    setup_database_constraints()
    #seed_admin_user()
    seed_doctor_users()     
   # generate_bulk_patient_data(5)