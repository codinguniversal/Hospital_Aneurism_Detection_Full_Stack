from pymongo import MongoClient
from app.config import static_settings

# ===== EDIT THESE TWO LINES =====
SCAN_ID = "SCN-2026-fdf9756d"          # The scan ID you want to fix
NEW_PATH = r"Whatever Path to an actual zip file"  # The FULL path to your existing zip file
# =================================

# Connect to MongoDB
client = MongoClient(static_settings.mongodb_uri)
db = client[static_settings.mongodb_db_name]
patients_collection = db["patients"]

# Update only that specific scan inside its patient
result = patients_collection.update_one(
    {"scans.id": SCAN_ID},
    {"$set": {"scans.$.img_file_path": NEW_PATH}}
)

if result.modified_count > 0:
    print(f"✅ Successfully updated scan {SCAN_ID} to: {NEW_PATH}")
else:
    print(f"❌ Scan {SCAN_ID} not found or path already matches.")