from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role, guardian_of

router = APIRouter(prefix="/api/exams", tags=["exams"])

class ExamIn(BaseModel):
    subject_id: int
    level: str
    title: str
    time_limit_min: int = 90

class QuestionIn(BaseModel):
    prompt: str
    options: list[str]
    answer: str
    skill: str | None = None

# ---- Creación (profesores/admin) ----
@router.post("")
def create_exam(data: ExamIn,
                user: models.User = Depends(require_role("profesor", "admin")),
                db: Session = Depends(get_db)):
    e = models.Exam(subject_id=data.subject_id, level=data.level,
                    title=data.title, time_limit_min=data.time_limit_min)
    db.add(e); db.commit(); db.refresh(e)
    return {"id": e.id}

@router.post("/{exam_id}/questions")
def add_question(exam_id: int, data: QuestionIn,
                 user: models.User = Depends(require_role("profesor", "admin")),
                 db: Session = Depends(get_db)):
    q = models.Question(exam_id=exam_id, prompt=data.prompt,
                        options=data.options, answer=data.answer,
                        skill=data.skill)
    db.add(q); db.commit()
    return {"id": q.id}

# ---- Catálogo de simulaciones ----
@router.get("")
def catalog(level: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Exam).filter_by(is_simulation=True)
    if level:
        q = q.filter_by(level=level)
    return [{"id": e.id, "title": e.title, "level": e.level,
             "time_limit_min": e.time_limit_min} for e in q.all()]

# ---- Rendición: entrega SOLO las preguntas, nunca la respuesta ----
@router.get("/{exam_id}/start")
def start(exam_id: int, db: Session = Depends(get_db)):
    qs = (db.query(models.Question).filter_by(exam_id=exam_id)
          .order_by(models.Question.order_idx).all())
    return {"exam_id": exam_id,
            "questions": [{"id": q.id, "prompt": q.prompt, "options": q.options}
                          for q in qs]}

# ---- Evaluación automática ----
@router.post("/{exam_id}/submit")
def submit(exam_id: int, student_id: int, answers: dict[str, str],
           user: models.User = Depends(require_role("apoderado", "admin", "alumno")),
           db: Session = Depends(get_db)):
    if user.role == "apoderado":
        guardian_of(student_id, user, db)
    qs = db.query(models.Question).filter_by(exam_id=exam_id).all()
    if not qs:
        raise HTTPException(404, "Simulación sin preguntas")
    correct = sum(1 for q in qs if answers.get(str(q.id)) == q.answer)
    score = round(correct / len(qs) * 100, 2)
    att = models.ExamAttempt(student_id=student_id, exam_id=exam_id,
                             finished_at=datetime.utcnow(), score=score,
                             answers=answers)
    db.add(att); db.commit(); db.refresh(att)
    return {"attempt_id": att.id, "score": score, "total": len(qs),
            "correct": correct}
