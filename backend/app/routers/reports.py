from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models
from ..security import require_role, guardian_of

router = APIRouter(prefix="/api/reports", tags=["reports"])

# Progreso del alumno: avance de lecciones + historial de simulaciones
@router.get("/student/{student_id}")
def student_report(student_id: int,
                   user: models.User = Depends(require_role("apoderado", "profesor", "admin")),
                   db: Session = Depends(get_db)):
    if user.role == "apoderado":
        guardian_of(student_id, user, db)

    enrollments = (db.query(models.Course)
                   .join(models.Enrollment, models.Enrollment.course_id == models.Course.id)
                   .filter(models.Enrollment.student_id == student_id).all())

    prog = (db.query(models.Progress.lesson_id, models.Progress.status)
            .filter_by(student_id=student_id).all())
    done = sum(1 for _, s in prog if s == "completed")

    attempts = (db.query(models.ExamAttempt, models.Exam)
                .join(models.Exam, models.Exam.id == models.ExamAttempt.exam_id)
                .filter(models.ExamAttempt.student_id == student_id)
                .order_by(models.ExamAttempt.finished_at.desc()).limit(20).all())

    avg = (db.query(func.avg(models.ExamAttempt.score))
           .filter_by(student_id=student_id).scalar())

    return {
        "student_id": student_id,
        "courses": [{"id": c.id, "title": c.title} for c in enrollments],
        "lessons_completed": done,
        "lessons_total": len(prog),
        "exam_average": float(avg) if avg else None,
        "recent_attempts": [
            {"exam": e.title, "score": float(a.score), "date": str(a.finished_at)}
            for a, e in attempts],
    }
