import random
import uuid
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from faker import Faker

from app.config import static_settings
from app.infrastructure.security.hashing import get_password_hash

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

# Track credentials in plain text to display at the very end
credentials_log = []

def setup_database_constraints():
    """Establishes unique identifier constraints on the database collections."""
    print("Enforcing unique constraint database indexes...")
    users_collection.create_index([("email", ASCENDING)], unique=True)
    users_collection.create_index([("employee_id", ASCENDING)], unique=True)

def seed_admin_user(current_id_num):
    """Seeds a primary administrator record with a sequential 6-digit ID."""
    print("Seeding admin user record...")
    
    # Format sequential number to 6 digits (e.g., 1 -> "000001")
    employee_id = f"{current_id_num:06d}"
    admin_email = "admin@hospital.com"
    raw_password = "SuperSecretAdmin2026!"
    
    admin_payload = {
        "employee_id": employee_id,
        "email": admin_email,
        "password": get_password_hash(raw_password),
        "role": "Admin"
    }
    
    users_collection.update_one({"email": admin_email}, {"$set": admin_payload}, upsert=True)
    
    credentials_log.append({
        "role": "admin",
        "employee_id": employee_id,
        "email": admin_email,
        "password": raw_password
    })
    print("Admin user seeded successfully.")
    return current_id_num + 1

def seed_doctor_users(start_id_num):
    """Seeds doctor records using sequential 6-digit IDs."""
    print("Seeding doctor user records...")
    
    current_id = start_id_num
    doctor_blueprints = [
        {"email": "smith@hospital.com", "password": "DoctorSmith2026!", "role": "Radiologist"},
        {"email": "neuro1@hospital.com", "password": "NeuroPassword2026!", "role": "Radiologist"}
    ]
    
    seeded_doctor_ids = []
    
    for doc in doctor_blueprints:
        employee_id = f"{current_id:06d}" # Format to 6 digits (e.g., "000002")
        seeded_doctor_ids.append(employee_id)
        
        doc_payload = {
            "employee_id": employee_id,
            "email": doc["email"],
            "password": get_password_hash(doc["password"]),
            "role": doc["role"]
        }
        
        users_collection.update_one(
            {"employee_id": employee_id}, 
            {"$set": doc_payload}, 
            upsert=True
        )
        
        credentials_log.append({
            "role": doc["role"],
            "employee_id": employee_id,
            "email": doc["email"],
            "password": doc["password"]
        })
        current_id += 1
        
    print(f"Successfully seeded {len(doctor_blueprints)} doctor records.")
    return seeded_doctor_ids

def generate_bulk_patient_data(assigned_doctors, num_records=5):
    """Generates bulk dummy patient cases assigned to our seeded 6-digit doctor IDs."""
    print(f"Generating {num_records} dummy patient records...")
    seeded_documents = []
    
    for _ in range(num_records):
        patient_id = f"PT-{random.randint(10000, 99999)}"
        scan_id = f"SCN-2026-{str(uuid.uuid4())[:8]}"
        
        doc = {
            "_id": patient_id,
            "patient_name": fake.name(),
            "birth_date": fake.date_of_birth(minimum_age=25, maximum_age=75).strftime("%Y-%m-%d"),
            # Randomly picks one of the actual 6-digit doctor IDs we created!
            "assigned_doc": random.choice(assigned_doctors),
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

def print_credentials_summary():
    """Prints a clean tabular terminal log showing the unencrypted passwords."""
    print("\n" + "="*70)
    print("                SEED USER CREDENTIALS SUMMARY")
    print("="*70)
    print(f"{'ROLE':<10} | {'EMPLOYEE ID':<12} | {'EMAIL':<22} | {'PLAIN PASSWORD'}")
    print("-"*70)
    for cred in credentials_log:
        print(f"{cred['role'].upper():<10} | {cred['employee_id']:<12} | {cred['email']:<22} | {cred['password']}")
    print("="*70 + "\n")

if __name__ == "__main__":
    print("Wiping old collections and indexes...")
    db.drop_collection("users")
    db.drop_collection("patients")

    setup_database_constraints()
    
    # Core ID tracking index counter
    next_id = 1
    
    # 1. Seed admin ("000001")
    next_id = seed_admin_user(current_id_num=next_id)
    
    # 2. Seed doctors ("000002", "000003")
    doctor_ids = seed_doctor_users(start_id_num=next_id)
    
    # 3. Seed patients linked to those doctor IDs
    generate_bulk_patient_data(assigned_doctors=doctor_ids, num_records=5)
    
    # 4. Display the plain credentials log
    print_credentials_summary()