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

class ScheduleBase(BaseModel):
    classId: int
    day: str
    lessons: List[str]

class Schedule(ScheduleBase):
    id: int
    className: Optional[str] = None 

db = []

async def get_class_name(class_id: int) -> str:
    async with httpx.AsyncClient() as client:
        try:
            disc_resp = await client.get(f"{DISCOVERY_URL}/services/class-service")
            if disc_resp.status_code != 200: return "Unknown (Service Down)"
            
            instances = disc_resp.json()
            if not instances: return "Unknown (No Instances)"
            
            target = random.choice(instances)
            url = f"http://{target['host']}:{target['port']}/classes"
            
            # Отримуємо всі класи і шукаємо потрібний (спрощена логіка)
            classes_resp = await client.get(url)
            if classes_resp.status_code == 200:
                classes = classes_resp.json()
                for c in classes:
                    if c['id'] == class_id:
                        return c['name']
            return "Unknown Class"
        except:
            return "Error Connecting"

@app.get("/schedules", response_model=List[Schedule])
def get_all(): return db

@app.post("/schedules", response_model=Schedule)
async def create(data: ScheduleBase):
    class_name = await get_class_name(data.classId)
    # FIX: Правильний автоінкремент
    new_id = max([s.id for s in db], default=0) + 1
    
    new_obj = Schedule(id=new_id, className=class_name, **data.dict())
    db.append(new_obj)
    return new_obj

@app.delete("/schedules/{id}")
def delete_schedule(id: int):
    global db
    initial_len = len(db)
    db = [s for s in db if s.id != id]
    if len(db) == initial_len:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVICE_PORT)