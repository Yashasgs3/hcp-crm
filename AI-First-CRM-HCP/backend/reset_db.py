import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

# Force delete old DB
db_path = "crm.db"
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Deleted {db_path}")
    except Exception as e:
        print(f"Could not delete: {e}")
        # Try renaming
        try:
            os.rename(db_path, db_path + ".old")
            print(f"Renamed to {db_path}.old")
        except Exception as e2:
            print(f"Could not rename either: {e2}")
else:
    print(f"{db_path} does not exist")

# Now create fresh tables
from app.config.init_db import create_tables
create_tables()
print("Fresh database created.")
