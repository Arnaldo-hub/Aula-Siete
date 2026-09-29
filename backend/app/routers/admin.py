from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role, hash_password
from ..bootstrap import run_seed, seed_banco_preguntas

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/reseed")
def reseed(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    r1 = run_seed(db)
    r2 = seed_banco_preguntas(db)
    return {"ok": True, **r1, **r2}

# ---- Estadisticas generales ----
@router.get("/stats")
def stats(user: models.User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    def count(model, **flt):
        return db.query(model).filter_by(**flt).count() if flt else db.query(model).count()
    avg = db.query(func.avg(models.ExamAttempt.score)).scalar()
    pts = db.query(func.coalesce(func.sum(models.ExamAttempt.score), 0)).scalar()
    return {
        "users_total": count(models.User),
        "users_apoderados": count(models.User, role="apoderado"),
        "users_profesores": count(models.User, role="profesor"),
        "students": count(models.Student),
        "courses": count(models.Course),
        "materials": count(models.Material),
        "recordings": count(models.Recording),
        "exams": count(models.Exam),
        "attempts": count(models.ExamAttempt),
        "attempts_avg": round(float(avg), 1) if avg else None,
        "attempts_points_total": int(pts or 0),
        "doubts_pending": db.query(models.Doubt).filter(models.Doubt.answer.is_(None)).count(),
        "subscriptions_active": db.query(models.Subscription).filter_by(status="authorized").count(),
        "subscriptions_total": count(models.Subscription),
    }

# ---- Todos los usuarios ----
@router.get("/users")
def list_users(role: str | None = None,
               user: models.User = Depends(require_role("admin")),
               db: Session = Depends(get_db)):
    q = db.query(models.User)
    if role:
        q = q.filter_by(role=role)
    rows = q.order_by(models.User.id.desc()).limit(300).all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role,
             "created": str(u.created_at)[:10]} for u in rows]

class NewUserIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str

@router.post("/users")
def create_user(data: NewUserIn,
                user: models.User = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    if data.role not in ("profesor", "apoderado", "admin"):
        raise HTTPException(400, "Rol invalido. Use: profesor, apoderado o admin.")
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(409, "El correo ya esta registrado.")
    u = models.User(email=data.email, full_name=data.full_name, role=data.role,
                    password_hash=hash_password(data.password))
    db.add(u); db.commit(); db.refresh(u)
    return {"id": u.id, "email": u.email, "role": u.role}

# ---- Todas las suscripciones ----
@router.get("/subscriptions")
def list_subs(user: models.User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    rows = (db.query(models.Subscription, models.User)
            .join(models.User, models.User.id == models.Subscription.guardian_id)
            .order_by(models.Subscription.id.desc()).limit(200).all())
    return [{"id": s.id, "guardian": g.email, "student_id": s.student_id, "plan": s.plan,
             "amount": float(s.amount), "status": s.status, "date": str(s.created_at)[:10]}
            for s, g in rows]
