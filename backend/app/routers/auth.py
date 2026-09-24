from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import hash_password, verify_password, create_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "apoderado"   # solo registro público de apoderados

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str

@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if data.role != "apoderado":
        raise HTTPException(400, "Solo registro de apoderados habilitado")
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(409, "El correo ya está registrado")
    user = models.User(email=data.email, password_hash=hash_password(data.password),
                       full_name=data.full_name, role="apoderado")
    db.add(user); db.commit(); db.refresh(user)
    return TokenOut(access_token=create_token(user.id, user.role),
                    role=user.role, full_name=user.full_name)

@router.post("/login", response_model=TokenOut)
async def login(request: Request, db: Session = Depends(get_db)):
    # Acepta JSON (frontend) o formulario (Swagger UI / OAuth2 password flow)
    ct = request.headers.get("content-type", "")
    if ct.startswith("application/json"):
        body = await request.json()
        email, password = body.get("email"), body.get("password")
    else:
        form = await request.form()
        email, password = form.get("username"), form.get("password")
    if not email or not password:
        raise HTTPException(401, "Credenciales inválidas")
    user = db.query(models.User).filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Credenciales inválidas")
    return TokenOut(access_token=create_token(user.id, user.role),
                    role=user.role, full_name=user.full_name)
