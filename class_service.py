from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Class Service", version="1.0.0")

# --- DTOs ---
class SchoolClassBase(BaseModel):
    name: str  # Наприклад "10-A"
    profile: Optional[str] = None # Наприклад "Math"

class SchoolClass(SchoolClassBase):
    id: int

# --- Repository (Data Layer) ---
class ClassRepository:
    def __init__(self):
        self._db = [
            SchoolClass(id=1, name="10-A", profile="Science"),
            SchoolClass(id=2, name="11-B", profile="Humanities")
        ]

    def get_all(self) -> List[SchoolClass]:
        return self._db

    def get_by_id(self, id: int) -> Optional[SchoolClass]:
        return next((c for c in self._db if c.id == id), None)

    def add(self, data: SchoolClassBase) -> SchoolClass:
        new_id = self._db[-1].id + 1 if self._db else 1
        new_obj = SchoolClass(id=new_id, **data.dict())
        self._db.append(new_obj)
        return new_obj

# --- Service (Business Logic) ---
class ClassService:
    def __init__(self, repo: ClassRepository):
        self.repo = repo

    def get_classes(self):
        return self.repo.get_all()

    def get_class(self, id: int):
        c = self.repo.get_by_id(id)
        if not c:
            raise HTTPException(status_code=404, detail="Class not found")
        return c

    def create_class(self, data: SchoolClassBase):
        return self.repo.add(data)

# --- Controller (Router) ---
repo = ClassRepository()
service = ClassService(repo)
router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("", response_model=List[SchoolClass])
def get_all():
    return service.get_classes()

@router.get("/{id}", response_model=SchoolClass)
def get_one(id: int):
    return service.get_class(id)

@router.post("", response_model=SchoolClass)
def create(data: SchoolClassBase):
    return service.create_class(data)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)