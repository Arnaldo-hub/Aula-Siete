from datetime import date
import secrets
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role, hash_password

router = APIRouter(prefix="/api/users", tags=["users"])

class StudentIn(BaseModel):
    run: str | None = None
    birth_date: str | None = None
    level: str
    full_name: str | None = None

def _student_out(s, db):
    name = None
    if s.user_id:
        u = db.get(models.User, s.user_id)
        name = u.full_name if u else None
    return {"id": s.id, "level": s.level, "name": name or f"Alumno #{s.id}",
            "birth_date": str(s.birth_date) if s.birth_date else None,
            "run": s.run}

@router.post("/students")
def create_student(data: StudentIn,
                   user=Depends(require_role("apoderado", "admin")),
                   db: Session = Depends(get_db)):
    birth = date.fromisoformat(data.birth_date) if data.birth_date else None
    run_clean = (data.run or "").strip() or None   # vacio -> NULL (sin RUN)
    st = models.Student(guardian_id=user.id, run=run_clean,
                        birth_date=birth, level=data.level)
    if data.full_name:
        base = (run_clean or secrets.token_hex(4)).replace(".", "").replace("-", "")
        email = f"alumno.{base}@alumno.aulasiete.cl"
        if db.query(models.User).filter_by(email=email).first():
            email = f"alumno.{secrets.token_hex(4)}@alumno.aulasiete.cl"
        u = models.User(email=email, full_name=data.full_name, role="alumno",
                        password_hash=hash_password(secrets.token_urlsafe(12)))
        db.add(u); db.flush()
        st.user_id = u.id
    db.add(st); db.commit(); db.refresh(st)
    return {"id": st.id, "level": st.level, "name": data.full_name}

@router.get("/students")
def my_students(user=Depends(require_role("apoderado", "admin", "profesor")),
                db: Session = Depends(get_db)):
    q = db.query(models.Student)
    if user.role == "apoderado":
        q = q.filter_by(guardian_id=user.id)
    return [_student_out(s, db) for s in q.all()]
