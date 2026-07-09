"""
Startup script: initializes the database and runs the FastAPI server.
"""
import os
import sys

# Ensure we're in the backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from app.config.init_db import create_tables

print("Initializing database...")
create_tables()
print("Database ready.")

if __name__ == "__main__":
    import uvicorn
    print("Starting server at http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
