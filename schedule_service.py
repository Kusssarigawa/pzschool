from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List, Optional
import requests
import uvicorn

app = FastAPI(title="Schedule Service", version="1.0.0")

# Конфігурація інших сервісів
CLASS_SERVICE_URL = "http://127.0.0.1:8001"

# --- DTOs ---
class Lesson(BaseModel):
    subjectName: str
    teacherName: str
    room: str
    startTime: str
    endTime: str

class DaySchedule(BaseModel):
    dayOfWeek: str
    lessons: List[Lesson]

class ScheduleBase(BaseModel):
    classId: int  # Зв'язок з сервісом класів за ID
    daySchedules: List[DaySchedule]

class Schedule(ScheduleBase):
    id: int
    className: Optional[str] = None # Це поле ми заповнимо, діставши дані з іншого сервісу

# --- Repository ---
class ScheduleRepository:
    def __init__(self):
        self._db = []
    
    def get_all(self): return self._db
    def get_by_id(self, id: int): return next((s for s in self._db if s.id == id), None)
    def add(self, data: ScheduleBase, class_name: str):
        new_id = self._db[-1].id + 1 if self._db else 1
        # Створюємо об'єкт і зберігаємо назву класу, яку отримали з мікросервісу
        new_obj = Schedule(id=new_id, className=class_name, **data.dict())
        self._db.append(new_obj)
        return new_obj

# --- Service (Inter-service communication here) ---
class ScheduleService:
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo
    
    def validate_class_exists(self, class_id: int) -> str:
        """
        Синхронний виклик до Class Service (8001).
        Повертає назву класу або викликає помилку.
        """
        try:
            response = requests.get(f"{CLASS_SERVICE_URL}/classes/{class_id}")
            if response.status_code == 200:
                class_data = response.json()
                return class_data['name']
            else:
                raise HTTPException(status_code=400, detail=f"Class with ID {class_id} does not exist in ClassService")
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail="Class Service is unavailable")

    def create_schedule(self, data: ScheduleBase):
        # 1. Мікросервісна взаємодія: перевірка класу
        class_name = self.validate_class_exists(data.classId)
        
        # 2. Якщо все ок, зберігаємо
        return self.repo.add(data, class_name)

    def get_all(self): return self.repo.get_all()
    def get_one(self, id: int):
        s = self.repo.get_by_id(id)
        if not s: raise HTTPException(404, "Schedule not found")
        return s

# --- Controller ---
repo = ScheduleRepository()
service = ScheduleService(repo)
router = APIRouter(prefix="/schedules", tags=["Schedules"])

@router.get("", response_model=List[Schedule])
def get_schedules(): return service.get_all()

@router.post("", response_model=Schedule)
def create_schedule(data: ScheduleBase):
    return service.create_schedule(data)

@router.get("/{id}", response_model=Schedule)
def get_schedule(id: int): return service.get_one(id)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)