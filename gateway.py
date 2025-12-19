import uvicorn
from fastapi import FastAPI, Request, HTTPException, Response
import httpx
import random

app = FastAPI(title="API Gateway")

DISCOVERY_URL = "http://127.0.0.1:8000"

async def get_service_url(service_name: str) -> str:
    """Запитує у Discovery адресу сервісу"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{DISCOVERY_URL}/services/{service_name}")
            if resp.status_code != 200:
                raise HTTPException(status_code=503, detail=f"Service '{service_name}' unavailable")
            
            instances = resp.json()
            # Простий Load Balancing (Random)
            target = random.choice(instances)
            return f"http://{target['host']}:{target['port']}"
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Discovery Service unavailable")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    """
    Маршрутизація:
    /classes/... -> class-service
    /teachers/... -> teacher-service
    /schedules/... -> schedule-service
    """
    path_parts = path.split("/")
    if not path_parts:
         raise HTTPException(status_code=400, detail="Invalid path")
    
    root_path = path_parts[0] # classes, teachers або schedules
    
    # Мапинг шляхів до імен сервісів в Discovery
    service_map = {
        "classes": "class-service",
        "teachers": "teacher-service",
        "schedules": "schedule-service"
    }
    
    service_name = service_map.get(root_path)
    if not service_name:
        raise HTTPException(status_code=404, detail="Service route not found")
        
    base_url = await get_service_url(service_name)
    target_url = f"{base_url}/{path}"
    
    # Проксування запиту
    async with httpx.AsyncClient() as client:
        try:
            proxy_req = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers, # Можна фільтрувати заголовки при потребі
                content=await request.body(),
                params=request.query_params
            )
            return Response(
                content=proxy_req.content,
                status_code=proxy_req.status_code,
                headers=proxy_req.headers
            )
        except httpx.RequestError:
             raise HTTPException(status_code=502, detail="Bad Gateway: Failed to connect to backend service")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)