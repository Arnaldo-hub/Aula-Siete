"""Carga de datos iniciales/demo. Idempotente: puede ejecutarse varias veces."""
from sqlalchemy.orm import Session
from . import models
from .security import hash_password

DEMO_PASSWORD = "demo1234"

def _user(db: Session, email: str, name: str, role: str):
    u = db.query(models.User).filter_by(email=email).first()
    if not u:
        u = models.User(email=email, full_name=name, role=role,
                        password_hash=hash_password(DEMO_PASSWORD))
        db.add(u); db.commit(); db.refresh(u)
    return u

def run_seed(db: Session) -> dict:
    admin = _user(db, "admin@aulasite.cl", "Admin Aula Site", "admin")
    prof = _user(db, "profesor@demo.cl", "Prof. Carolina Rojas", "profesor")
    guard = _user(db, "apoderado@demo.cl", "Maria Perez", "apoderado")

    subj = db.query(models.Subject).filter_by(name="Matematica", level="MEDIA_1").first()
    if not subj:
        subj = models.Subject(name="Matematica", level="MEDIA_1")
        db.add(subj); db.commit(); db.refresh(subj)

    course = db.query(models.Course).first()
    if not course:
        course = models.Course(subject_id=subj.id, level="MEDIA_1",
                               teacher_id=prof.id, title="Matematica 1 Medio",
                               description="Preparacion examen libre")
        db.add(course); db.commit(); db.refresh(course)

    exam = db.query(models.Exam).first()
    if not exam:
        exam = models.Exam(subject_id=subj.id, level="MEDIA_1",
                           title="Simulacion Examen Libre - Matematica 1 Medio")
        db.add(exam); db.commit(); db.refresh(exam)
        db.add_all([
            models.Question(exam_id=exam.id,
                            prompt="Cuanto es 3x + 2x cuando x=4?",
                            options=["20", "22", "24", "18"], answer="20",
                            skill="OA 7 - Algebra"),
            models.Question(exam_id=exam.id, prompt="Raiz cuadrada de 144:",
                            options=["10", "11", "12", "14"], answer="12",
                            skill="OA 3 - Numeros"),
        ])
        db.commit()

    # Alumno demo del apoderado (se crea aunque el seed parcial haya corrido antes)
    st = db.query(models.Student).filter_by(guardian_id=guard.id).first()
    if not st:
        st = models.Student(guardian_id=guard.id, level="MEDIA_1")
        db.add(st); db.flush()
    enr = db.query(models.Enrollment).filter_by(student_id=st.id, course_id=course.id).first()
    if not enr:
        db.add(models.Enrollment(student_id=st.id, course_id=course.id))
    db.commit()
    return {"ok": True, "admin_id": admin.id, "student_id": st.id,
            "course_id": course.id, "exam_id": exam.id}
