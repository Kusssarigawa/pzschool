from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="Teacher Service", version="1.0.0")

# --- DTOs ---
class TeacherBase(BaseModel):
    fullName: str
    subjectSpecialization: str

class Teacher(TeacherBase):
    id: int

# --- Repository ---
class TeacherRepository:
    def __init__(self):
        self._db = [
            Teacher(id=1, fullName="Mr. Johnson", subjectSpecialization="History"),
            Teacher(id=2, fullName="Mrs. Smith", subjectSpecialization="Math")
        ]
    
    def get_all(self): return self._db
    def get_by_id(self, id: int): return next((t for t in self._db if t.id == id), None)
    def add(self, data: TeacherBase):
        new_id = self._db[-1].id + 1 if self._db else 1
        new_obj = Teacher(id=new_id, **data.dict())
        self._db.append(new_obj)
        return new_obj

# --- Service ---
class TeacherService:
    def __init__(self, repo: TeacherRepository):
        self.repo = repo
    
    def get_all(self): return self.repo.get_all()
    
    def get_one(self, id: int):
        t = self.repo.get_by_id(id)
        if not t: raise HTTPException(404, "Teacher not found")
        return t
    
    def create(self, data: TeacherBase): return self.repo.add(data)

# --- Controller ---
repo = TeacherRepository()
service = TeacherService(repo)
router = APIRouter(prefix="/teachers", tags=["Teachers"])

@router.get("", response_model=List[Teacher])
def get_teachers(): return service.get_all()

@router.get("/{id}", response_model=Teacher)
def get_teacher(id: int): return service.get_one(id)

@router.post("", response_model=Teacher)
def create_teacher(data: TeacherBase): return service.create(data)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)