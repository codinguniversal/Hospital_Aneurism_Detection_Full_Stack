import random
import uuid
from datetime import datetime
from pymongo import MongoClient
from faker import Faker

fake = Faker()

#  your local MongoDB server 
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["CAD_DB"]
collection = db["patients"]

# folder containing dicom images
scan_paths = [
    "E:/for database/Have Ane/1.zip",
    "E:/for database/Have Ane/5.zip",
    "E:/for database/normal/1.zip",
    "E:/for database/normal/2.zip"
]

def generate_bulk_data(num_records=5):
    seeded_documents = []
    
    for _ in range(num_records):
        # Auto-generate dynamic tracking string identifiers
        patient_id = f"PT-{random.randint(10000, 99999)}"
        scan_id = f"SCN-2026-{str(uuid.uuid4())[:8]}" # Uses a short UUID chunk for the scan
        
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
        
    # Bulk insert into MongoDB
    collection.insert_many(seeded_documents)
    print(f"Successfully seeded {num_records} dynamic patient documents into CAD_DB!")

if __name__ == "__main__":
    generate_bulk_data(5)
