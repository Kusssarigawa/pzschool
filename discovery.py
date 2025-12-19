import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import time

app = FastAPI(title="Discovery Service")

# Модель даних для реєстрації
class ServiceInstance(BaseModel):
    name: str
    host: str
    port: int
    last_heartbeat: float = 0.0

# Реєстр: { "service_name": [ServiceInstance, ServiceInstance] }
registry: Dict[str, List[ServiceInstance]] = {}

@app.post("/register")
def register(instance: ServiceInstance):
    # Якщо сервіс ще не в реєстрі, створюємо список
    if instance.name not in registry:
        registry[instance.name] = []
    
    # Видаляємо старий запис, якщо такий хост:порт вже є (оновлення)
    registry[instance.name] = [
        s for s in registry[instance.name] 
        if not (s.host == instance.host and s.port == instance.port)
    ]
    
    instance.last_heartbeat = time.time()
    registry[instance.name].append(instance)
    print(f"Registered: {instance.name} at {instance.host}:{instance.port}")
    return {"status": "registered"}

@app.get("/services/{name}")
def get_service(name: str):
    # Повертаємо тільки "живі" сервіси (тайм-аут 30 сек)
    current_time = time.time()
    if name not in registry:
        raise HTTPException(status_code=404, detail="Service not found")
    
    alive_instances = [
        s for s in registry[name] 
        if current_time - s.last_heartbeat < 30
    ]
    
    if not alive_instances:
        raise HTTPException(status_code=503, detail="No instances available")
        
    return alive_instances

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)