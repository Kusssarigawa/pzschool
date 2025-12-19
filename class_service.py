from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import httpx
import threading
import time

app = FastAPI(title="Class Service")

# --- Config ---
SERVICE_NAME = "class-service"
SERVICE_PORT = 8001
DISCOVERY_URL = "http://127.0.0.1:8000"

# --- Registration Logic ---
def register_in_discovery():
    while True:
        try:
            with httpx.Client() as client:
                client.post(f"{DISCOVERY_URL}/register", json={
                    "name": SERVICE_NAME,
                    "host": "127.0.0.1",
                    "port": SERVICE_PORT
                })
        except Exception as e:
            print(f"Failed to register: {e}")
        time.sleep(10) # Heartbeat кожні 10 сек

@app.on_event("startup")
async def startup_event():
    # Запускаємо реєстрацію в окремому потоці
    thread = threading.Thread(target=register_in_discovery, daemon=True)
    thread.start()

# --- Business Logic (Same as before) ---
class SchoolClass(BaseModel):
    id: int
    name: str
    profile: Optional[str] = None

db = [
    SchoolClass(id=1, name="10-A", profile="Science"),
    SchoolClass(id=2, name="11-B", profile="Humanities")
]

@app.get("/classes", response_model=List[SchoolClass])
def get_all(): return db

@app.get("/classes/{id}", response_model=SchoolClass)
def get_one(id: int):
    return next((c for c in db if c.id == id), None)

@app.post("/classes", response_model=SchoolClass)
def create(data: SchoolClass):
    # АВТОМАТИЧНА ГЕНЕРАЦІЯ ID
    new_id = db[-1].id + 1 if db else 1
    
    data.id = new_id
    
    db.append(data)
    return data

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVICE_PORT)