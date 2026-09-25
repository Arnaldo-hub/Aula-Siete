from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role, guardian_of

router = APIRouter(prefix="/api/doubts", tags=["doubts"])

class DoubtIn(BaseModel):
    student_id: int
    question: str

class AnswerIn(BaseModel):
    answer: str

@router.post("")
def ask(data: DoubtIn,
        user: models.User = Depends(require_role("apoderado", "admin", "alumno")),
        db: Session = Depends(get_db)):
    if user.role == "apoderado":
        guardian_of(data.student_id, user, db)
    d = models.Doubt(student_id=data.student_id, asked_by=user.id, question=data.question)
    db.add(d); db.commit(); db.refresh(d)
    return {"id": d.id}

@router.get("")
def list_doubts(pending: bool = False,
                user: models.User = Depends(require_role("apoderado", "profesor", "admin")),
                db: Session = Depends(get_db)):
    q = db.query(models.Doubt)
    if user.role == "apoderado":
        my_ids = [s.id for s in db.query(models.Student).filter_by(guardian_id=user.id)]
        q = q.filter(models.Doubt.student_id.in_(my_ids or [-1]))
    if pending:
        q = q.filter(models.Doubt.answer.is_(None))
    rows = q.order_by(models.Doubt.created_at.desc()).limit(50).all()
    return [{"id": r.id, "student_id": r.student_id, "question": r.question,
             "answer": r.answer, "date": str(r.created_at)[:16]} for r in rows]

@router.post("/{doubt_id}/answer")
def answer(doubt_id: int, data: AnswerIn,
           user: models.User = Depends(require_role("profesor", "admin")),
           db: Session = Depends(get_db)):
    d = db.get(models.Doubt, doubt_id)
    if not d:
        raise HTTPException(404, "Duda no encontrada")
    d.answer = data.answer
    d.answered_at = datetime.utcnow()
    db.commit()
    return {"ok": True}
