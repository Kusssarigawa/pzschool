from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="School Schedule API", version="2.0.0")

# ==========================
# 1. DTO / ENTITIES (Моделі даних)
# ==========================

class Subject(BaseModel):
    subjectNumber: int
    subjectName: str
    teacher: Optional[str] = None
    room: Optional[str] = None
    startTime: str
    endTime: str

class Lesson(BaseModel):
    subject: Optional[Subject] = None
    break_activity: Optional[str] = None

class DaySchedule(BaseModel):
    dayOfWeek: str
    lessons: List[Lesson]

class SchoolSchedule(BaseModel):
    id: int
    profile: Optional[str] = None
    className: str
    classroomTeacher: Optional[str] = None
    daySchedules: List[DaySchedule] = []

# ==========================
# 2. DATA/REPOSITORY LAYER (Робота з даними)
# ==========================
# Відповідає вимозі: "Реалізовано зберігання даних... Data/Repository"

class ScheduleRepository:
    def __init__(self):
        self._db: List[SchoolSchedule] = []

    def get_all(self) -> List[SchoolSchedule]:
        return self._db

    def get_by_id(self, s_id: int) -> Optional[SchoolSchedule]:
        for s in self._db:
            if s.id == s_id:
                return s
        return None

    def add(self, schedule: SchoolSchedule):
        self._db.append(schedule)
        return schedule

    def update(self, s_id: int, updated_schedule: SchoolSchedule) -> Optional[SchoolSchedule]:
        for index, s in enumerate(self._db):
            if s.id == s_id:
                # Оновлюємо, зберігаючи ID (або замінюємо повністю)
                self._db[index] = updated_schedule
                return updated_schedule
        return None

    def delete(self, s_id: int) -> bool:
        for index, s in enumerate(self._db):
            if s.id == s_id:
                del self._db[index]
                return True
        return False

# Створюємо екземпляр репозиторія
repository = ScheduleRepository()

# ==========================
# 3. SERVICE LAYER (Бізнес-логіка)
# ==========================
# Відповідає вимозі: "Service (бізнес-логіка)"

class ScheduleService:
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    def get_schedules(self, class_name_filter: Optional[str] = None) -> List[SchoolSchedule]:
        all_schedules = self.repo.get_all()
        if class_name_filter:
            # Фільтрація за назвою класу (вимога Query Parameters)
            return [s for s in all_schedules if s.className == class_name_filter]
        return all_schedules

    def get_schedule(self, s_id: int) -> SchoolSchedule:
        schedule = self.repo.get_by_id(s_id)
        if not schedule:
            raise HTTPException(status_code=404, detail=f"Schedule with ID {s_id} not found")
        return schedule

    def create_schedule(self, schedule: SchoolSchedule) -> SchoolSchedule:
        if self.repo.get_by_id(schedule.id):
            raise HTTPException(status_code=400, detail="Schedule with this ID already exists")
        return self.repo.add(schedule)

    def update_schedule(self, s_id: int, schedule: SchoolSchedule) -> SchoolSchedule:
        # Перевірка, що ID в шляху співпадає з ID в тілі (бізнес-правило)
        if s_id != schedule.id:
            raise HTTPException(status_code=400, detail="ID in path and body must match")
        
        updated = self.repo.update(s_id, schedule)
        if not updated:
            raise HTTPException(status_code=404, detail="Schedule not found for update")
        return updated

    def delete_schedule(self, s_id: int):
        success = self.repo.delete(s_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found for deletion")
        return {"detail": "Schedule deleted successfully"}

service = ScheduleService(repository)

# ==========================
# 4. CONTROLLER LAYER (Обробка запитів)
# ==========================
# Відповідає вимозі: "Controller (обробка зовнішніх викликів)"

# 1. GET ALL (з фільтрацією)
@app.get("/schedules", response_model=List[SchoolSchedule], summary="Отримати всі розклади (з фільтрацією)")
def get_schedules(class_name: Optional[str] = Query(None, description="Фільтр за назвою класу")):
    return service.get_schedules(class_name)

# 2. GET BY ID (Path Variable)
@app.get("/schedules/{id}", response_model=SchoolSchedule, summary="Отримати розклад за ID")
def get_schedule_by_id(id: int = Path(..., description="ID розкладу")):
    return service.get_schedule(id)

# 3. POST (Створення)
@app.post("/schedules", response_model=SchoolSchedule, status_code=201, summary="Створити розклад")
def create_schedule(schedule: SchoolSchedule):
    return service.create_schedule(schedule)

# 4. PUT (Повне оновлення - вимога повного CRUD)
@app.put("/schedules/{id}", response_model=SchoolSchedule, summary="Оновити розклад")
def update_schedule(id: int, schedule: SchoolSchedule):
    return service.update_schedule(id, schedule)

# 5. DELETE (Видалення - вимога повного CRUD)
@app.delete("/schedules/{id}", summary="Видалити розклад")
def delete_schedule(id: int):
    return service.delete_schedule(id)

# 6. SUB-RESOURCE (Вкладений ресурс - вимога Sub-resource)
# Отримати тільки дні тижня для конкретного розкладу
@app.get("/schedules/{id}/days", response_model=List[DaySchedule], summary="Отримати дні розкладу (Sub-resource)")
def get_schedule_days(id: int):
    schedule = service.get_schedule(id)
    return schedule.daySchedules

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)