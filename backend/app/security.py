from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from . import models

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(p: str) -> str:
    return pwd.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd.verify(p, h)

def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2),
                     db: Session = Depends(get_db)) -> models.User:
    cred_err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise cred_err
    user = db.get(models.User, user_id)
    if not user:
        raise cred_err
    return user

def require_role(*roles: str):
    def checker(user: models.User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "Permisos insuficientes")
        return user
    return checker

# Acceso de apoderado a sus pupilos (protección de datos de menores)
def guardian_of(student_id: int, user: models.User, db: Session) -> None:
    if user.role == "admin":
        return
    if user.role != "apoderado":
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    owns = db.query(models.Student).filter_by(
        id=student_id, guardian_id=user.id).first()
    if not owns:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "No es apoderado de este alumno")
