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
def catalog(level: str | None = None, kind: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Exam).filter_by(is_simulation=True)
    if level:
        q = q.filter_by(level=level)
    if kind:
        q = q.filter_by(kind=kind)
    return [{"id": e.id, "title": e.title, "level": e.level, "kind": e.kind,
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


def _build_path(db: Session, student_id: int, exam_id: int, answers: dict) -> list:
    """A partir de las respuestas del diagnostico, crea items de ruta por OA debil."""
    qs = db.query(models.Question).filter_by(exam_id=exam_id).all()
    weak = []
    for q in qs:
        if answers.get(str(q.id)) != q.answer and q.oa:
            weak.append(q.oa)
    weak = list(dict.fromkeys(weak))   # unicos, conservando orden
    created = []
    for oa in weak:
        exists = db.query(models.PathItem).filter_by(student_id=student_id, oa=oa,
                                                     status="pending").first()
        if exists:
            continue
        mats = db.query(models.Material).filter_by(oa=oa).limit(2).all()
        if mats:
            for m in mats:
                db.add(models.PathItem(student_id=student_id, oa=oa, material_id=m.id,
                                       title=f"Reforzar {oa}: {m.title}"))
        else:
            db.add(models.PathItem(student_id=student_id, oa=oa, material_id=None,
                                   title=f"Reforzar {oa}: pide al docente material de esta unidad"))
        created.append(oa)
    db.commit()
    return created


class PathDone(BaseModel):
    pass


@router.get("/path/{student_id}")
def my_path(student_id: int,
            user: models.User = Depends(require_role("apoderado", "admin", "alumno")),
            db: Session = Depends(get_db)):
    if user.role == "apoderado":
        guardian_of(student_id, user, db)
    rows = (db.query(models.PathItem).filter_by(student_id=student_id)
            .order_by(models.PathItem.id.desc()).limit(60).all())
    return [{"id": r.id, "oa": r.oa, "title": r.title, "status": r.status,
             "material_id": r.material_id} for r in rows]


@router.post("/path/{item_id}/done")
def path_done(item_id: int,
              user: models.User = Depends(require_role("apoderado", "admin", "alumno")),
              db: Session = Depends(get_db)):
    item = db.get(models.PathItem, item_id)
    if not item:
        raise HTTPException(404, "Item no encontrado")
    if user.role == "apoderado":
        guardian_of(item.student_id, user, db)
    item.status = "completed"
    db.commit()
    return {"ok": True}
