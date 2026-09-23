from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import get_current_user, require_role

router = APIRouter(prefix="/api/users", tags=["users"])

class StudentIn(BaseModel):
    run: str | None = None
    birth_date: str | None = None
    level: str
    full_name: str | None = None   # si se crea cuenta de alumno

# Apoderado registra a sus alumnos (menores) — sin cuenta propia de login
@router.post("/students")
def create_student(data: StudentIn,
                   user: models.User = Depends(require_role("apoderado", "admin")),
                   db: Session = Depends(get_db)):
    st = models.Student(guardian_id=user.id, run=data.run,
                        birth_date=data.birth_date, level=data.level)
    db.add(st); db.commit(); db.refresh(st)
    return {"id": st.id, "level": st.level}

# Apoderado ve solo a SUS alumnos (privacidad de datos de menores)
@router.get("/students")
def my_students(user: models.User = Depends(require_role("apoderado", "admin", "profesor")),
                db: Session = Depends(get_db)):
    q = db.query(models.Student)
    if user.role == "apoderado":
        q = q.filter_by(guardian_id=user.id)
    return [{"id": s.id, "level": s.level, "birth_date": str(s.birth_date)}
            for s in q.all()]
