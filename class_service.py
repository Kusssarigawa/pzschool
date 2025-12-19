from fastapi import FastAPI, HTTPException
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

class SchoolClass(BaseModel):
    id: int
    name: str
    profile: Optional[str] = None

# Початкові дані
db = [
    SchoolClass(id=1, name="10-A", profile="Science"),
    SchoolClass(id=2, name="11-B", profile="Humanities")
]

@app.get("/classes", response_model=List[SchoolClass])
def get_all(): return db

@app.post("/classes", response_model=SchoolClass)
def create(data: SchoolClass):
    # FIX: Правильний автоінкремент
    new_id = max([c.id for c in db], default=0) + 1
    data.id = new_id
    db.append(data)
    return data

@app.delete("/classes/{id}")
def delete_class(id: int):
    global db
    initial_len = len(db)
    db = [c for c in db if c.id != id]
    if len(db) == initial_len:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVICE_PORT)