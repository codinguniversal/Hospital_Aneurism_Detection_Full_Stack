import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient, ASCENDING
from faker import Faker

from app.config import static_settings
from app.infrastructure.security.hashing import get_password_hash

fake = Faker()

client = MongoClient(static_settings.mongodb_uri)
db = client[static_settings.mongodb_db_name]

patients_collection = db["patients"]
users_collection = db["users"]
counters_collection = db["counters"]

# Only these two parent folders need to be configured.
NEGATIVE_ZIP_PARENT = Path(
    r"C:\Users\20220\Documents\Codex\RSNA-Aneurysm-Detection"
    r"\clear filter\rsna_10_negative_normal_fast_ALL(1)"
)
POSITIVE_ZIP_PARENT = Path(
    r"C:\Users\20220\Documents\Codex\RSNA-Aneurysm-Detection"
    r"\clear filter\rsna_10_positive_fast_ALL(1)"
)

NEGATIVE_PREFERRED_SUFFIXES = ("3173", "2462", "0739")
POSITIVE_PREFERRED_SUFFIXES = ("5099", "5466", "3656")

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

def select_scan_archives(parent_folder, preferred_suffixes, count=3):
    """Select preferred ZIP suffixes, filling absent slots with random ZIPs."""
    parent_folder = Path(parent_folder).expanduser().resolve()
    if not parent_folder.is_dir():
        raise FileNotFoundError(f"Scan parent folder does not exist: {parent_folder}")

    candidates = sorted(path for path in parent_folder.rglob("*.zip") if path.is_file())
    if len(candidates) < count:
        raise ValueError(
            f"Expected at least {count} ZIP files in {parent_folder}, found {len(candidates)}."
        )

    selected = []
    for suffix in preferred_suffixes:
        preferred = next(
            (path for path in candidates if path.stem.endswith(suffix) and path not in selected),
            None,
        )
        if preferred:
            selected.append(preferred)

    remaining = [path for path in candidates if path not in selected]
    selected.extend(random.sample(remaining, count - len(selected)))
    return selected


def build_scan_paths():
    negative_paths = select_scan_archives(
        NEGATIVE_ZIP_PARENT,
        NEGATIVE_PREFERRED_SUFFIXES,
    )
    positive_paths = select_scan_archives(
        POSITIVE_ZIP_PARENT,
        POSITIVE_PREFERRED_SUFFIXES,
    )
    selected_paths = negative_paths + positive_paths
    random.shuffle(selected_paths)

    print("Selected DICOM archives:")
    for path in selected_paths:
        print(f"  - {path}")
    return selected_paths


def generate_bulk_patient_data(assigned_doctors, scan_paths):
    """Generates bulk dummy patient cases assigned to our seeded 6-digit doctor IDs."""
    num_records = len(scan_paths)
    print(f"Generating {num_records} dummy patient records...")
    seeded_documents = []
    
    for scan_path in scan_paths:
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
                    "scan_date": datetime.now(timezone.utc),
                    "status": "Pending",
                    "img_file_path": str(scan_path),
                    "results": {}
                }
            ]
        }
        seeded_documents.append(doc)
        
    patients_collection.insert_many(seeded_documents)
    print(f"Successfully seeded {num_records} dynamic patient documents!")

def initialize_employee_id_counter(employee_ids):
    """Keeps runtime ID generation aligned with users inserted by this seed."""
    highest_employee_id = max(int(employee_id) for employee_id in employee_ids)
    counters_collection.update_one(
        {"_id": "employee_id_sequence"},
        {"$set": {"seq": highest_employee_id}},
        upsert=True,
    )

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

    # Registration must continue at 000004 rather than reusing 000001.
    initialize_employee_id_counter(["000001", *doctor_ids])
    
    # 3. Seed patients linked to those doctor IDs
    generate_bulk_patient_data(
        assigned_doctors=doctor_ids,
        scan_paths=build_scan_paths(),
    )
    
    # 4. Display the plain credentials log
    print_credentials_summary()
