from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role, hash_password
from ..bootstrap import run_seed, seed_banco_preguntas

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/reseed")
def reseed(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Recarga/verifica datos demo y el banco de preguntas. Solo administradores."""
    r1 = run_seed(db)
    r2 = seed_banco_preguntas(db)
    return {"ok": True, **r1, **r2}

class NewUserIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str          # profesor | apoderado | admin

@router.post("/users")
def create_user(data: NewUserIn,
                user: models.User = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    """Crear cuentas de profesores (o apoderados/admin). Solo administradores."""
    if data.role not in ("profesor", "apoderado", "admin"):
        raise HTTPException(400, "Rol invalido. Use: profesor, apoderado o admin.")
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(409, "El correo ya esta registrado.")
    u = models.User(email=data.email, full_name=data.full_name, role=data.role,
                    password_hash=hash_password(data.password))
    db.add(u); db.commit(); db.refresh(u)
    return {"id": u.id, "email": u.email, "role": u.role}
