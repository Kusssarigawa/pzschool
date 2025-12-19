from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
import httpx
import threading
import time

app = FastAPI(title="Teacher Service")

SERVICE_NAME = "teacher-service"
SERVICE_PORT = 8002
DISCOVERY_URL = "http://127.0.0.1:8000"

def register_in_discovery():
    while True:
        try:
            with httpx.Client() as client:
                client.post(f"{DISCOVERY_URL}/register", json={
                    "name": SERVICE_NAME,
                    "host": "127.0.0.1",
                    "port": SERVICE_PORT
                })
        except Exception: pass
        time.sleep(10)

@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=register_in_discovery, daemon=True)
    thread.start()

class Teacher(BaseModel):
    id: int
    fullName: str
    subject: str

db = [Teacher(id=1, fullName="Mr. Johnson", subject="History")]

@app.get("/teachers", response_model=List[Teacher])
def get_all(): return db

@app.post("/teachers")
def create(data: Teacher):
    # АВТОМАТИЧНА ГЕНЕРАЦІЯ ID
    # Беремо ID останнього вчителя і додаємо 1. Якщо список порожній - ставимо 1.
    new_id = db[-1].id + 1 if db else 1
    
    # Переписуємо ID в об'єкті
    data.id = new_id
    
    db.append(data)
    return data

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVICE_PORT)