from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db, SessionLocal
from . import models
from .routers import auth, users, courses, classes, exams, reports, admin, doubts, libro

app = FastAPI(title="Aula Site API",
              description="Plataforma de apoyo pedagogico para Examenes Libres (Chile)",
              version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth.router, users.router, courses.router,
          classes.router, exams.router, reports.router, admin.router, doubts.router, libro.router):
    app.include_router(r)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/stats")
def stats():
    """Contadores reales de la plataforma (para la pagina de inicio)."""
    db: Session = SessionLocal()
    try:
        return {
            "courses": db.query(models.Course).count(),
            "exams": db.query(models.Exam).count(),
            "questions": db.query(models.Question).count(),
            "recordings": db.query(models.Recording).count(),
            "attempts": db.query(models.ExamAttempt).count(),
        }
    finally:
        db.close()
