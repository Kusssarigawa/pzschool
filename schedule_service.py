from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import httpx
import threading
import time
import random

app = FastAPI(title="Schedule Service")

SERVICE_NAME = "schedule-service"
SERVICE_PORT = 8003
DISCOVERY_URL = "http://127.0.0.1:8000"

# --- Registration ---
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
    threading.Thread(target=register_in_discovery, daemon=True).start()

# --- Logic with Inter-service Communication ---

class ScheduleBase(BaseModel):
    classId: int
    day: str
    lessons: List[str]

class Schedule(ScheduleBase):
    id: int
    className: Optional[str] = None 

db = []

async def get_class_name(class_id: int) -> str:
    """
    Звертаємось до Discovery, щоб знайти адресу Class Service,
    а потім робимо запит до нього.
    """
    async with httpx.AsyncClient() as client:
        # 1. Запит до Discovery
        discovery_resp = await client.get(f"{DISCOVERY_URL}/services/class-service")
        if discovery_resp.status_code != 200:
            raise HTTPException(503, "Class Service discovery failed")
        
        # 2. Вибір екземпляра (Client-side Load Balancing)
        instances = discovery_resp.json()
        target = random.choice(instances)
        url = f"http://{target['host']}:{target['port']}/classes/{class_id}"
        
        # 3. Запит до Class Service
        class_resp = await client.get(url)
        if class_resp.status_code == 200:
            return class_resp.json()['name']
        return "Unknown Class"

@app.get("/schedules", response_model=List[Schedule])
def get_all(): return db

@app.post("/schedules", response_model=Schedule)
async def create(data: ScheduleBase):
    # Отримуємо назву класу через мікросервісний виклик
    class_name = await get_class_name(data.classId)
    
    new_obj = Schedule(id=len(db)+1, className=class_name, **data.dict())
    db.append(new_obj)
    return new_obj

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVICE_PORT)