from fastapi import FastAPI, HTTPException
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
                    "name": SERVICE_NAME, "host": "127.0.0.1", "port": SERVICE_PORT
                })
        except: pass
        time.sleep(10)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=register_in_discovery, daemon=True).start()

class Teacher(BaseModel):
    id: int
    fullName: str
    subject: str

db = [Teacher(id=1, fullName="Mr. Johnson", subject="History")]

@app.get("/teachers", response_model=List[Teacher])
def get_all(): return db

@app.post("/teachers", response_model=Teacher)
def create(data: Teacher):
    # FIX: Правильний автоінкремент
    new_id = max([t.id for t in db], default=0) + 1
    data.id = new_id
    db.append(data)
    return data

@app.delete("/teachers/{id}")
def delete_teacher(id: int):
    global db
    initial_len = len(db)
    db = [t for t in db if t.id != id]
    if len(db) == initial_len:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVICE_PORT)