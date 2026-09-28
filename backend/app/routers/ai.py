from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role, guardian_of
from ..ai import chat, SYSTEM_TUTOR, SYSTEM_GENERADOR, SYSTEM_ENSAYO

router = APIRouter(prefix="/api", tags=["ai"])

class TutorIn(BaseModel):
    message: str
    level: str = "MEDIA_4"
    student_id: int | None = None
    history: list[dict] = []

@router.post("/tutor/chat")
def tutor(data: TutorIn,
          user: models.User = Depends(require_role("apoderado", "admin", "alumno", "profesor")),
          db: Session = Depends(get_db)):
    weak = "ninguno registrado aun"
    if data.student_id:
        if user.role == "apoderado":
            guardian_of(data.student_id, user, db)
        rows = (db.query(models.PathItem).filter_by(student_id=data.student_id,
                                                    status="pending").limit(8).all())
        if rows:
            weak = ", ".join(r.oa for r in rows)
    system = SYSTEM_TUTOR.format(level=data.level, weak=weak)
    reply = chat(system, [{"role": "user" if m.get("from") != "bot" else "assistant",
                           "content": m.get("text", "")} for m in data.history]
                 + [{"role": "user", "content": data.message}])
    return {"reply": reply}

class GenIn(BaseModel):
    subject: str
    level: str
    oa: str | None = None
    topic: str
    kind: str = "guia"   # guia / planificacion / ejercicios

@router.post("/ai/generate")
def generate(data: GenIn,
             user: models.User = Depends(require_role("profesor", "admin"))):
    prompt = (f"Genera una {data.kind} de {data.subject} para nivel {data.level}, "
              f"topico: {data.topic}. " + (f"Objetivo de Aprendizaje (OA): {data.oa}." if data.oa else ""))
    reply = chat(SYSTEM_GENERADOR, [{"role": "user", "content": prompt}], max_tokens=1400)
    return {"content": reply}

class EssayIn(BaseModel):
    text: str
    level: str = "MEDIA_4"

@router.post("/ai/essay")
def essay(data: EssayIn,
          user: models.User = Depends(require_role("apoderado", "admin", "alumno", "profesor"))):
    prompt = (f"Corrige el siguiente ensayo escrito por un estudiante de {data.level}. "
              f"Texto:\n\n{data.text}")
    reply = chat(SYSTEM_ENSAYO, [{"role": "user", "content": prompt}], max_tokens=1200)
    return {"feedback": reply}
