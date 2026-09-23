"""Poblado inicial: usuarios demo, asignatura, curso y simulación de examen."""
from app.database import SessionLocal, engine, Base
from app import models
from app.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def user(email, name, role):
    u = db.query(models.User).filter_by(email=email).first()
    if not u:
        u = models.User(email=email, full_name=name, role=role,
                        password_hash=hash_password("demo1234"))
        db.add(u); db.commit(); db.refresh(u)
    return u

admin = user("admin@aulasite.cl", "Admin Aula Site", "admin")
prof = user("profesor@demo.cl", "Prof. Carolina Rojas", "profesor")
guard = user("apoderado@demo.cl", "María Pérez", "apoderado")

if not db.query(models.Subject).first():
    subj = models.Subject(name="Matemática", level="MEDIA_1")
    db.add(subj); db.commit()
    course = models.Course(subject_id=subj.id, level="MEDIA_1",
                           teacher_id=prof.id, title="Matemática 1° Medio",
                           description="Preparación examen libre")
    db.add(course); db.commit()
    exam = models.Exam(subject_id=subj.id, level="MEDIA_1",
                       title="Simulación Examen Libre — Matemática 1° Medio")
    db.add(exam); db.commit()
    db.add_all([
        models.Question(exam_id=exam.id, prompt="¿Cuánto es 3x + 2x cuando x=4?",
                        options=["20", "22", "24", "18"], answer="20",
                        skill="OA 7 - Álgebra"),
        models.Question(exam_id=exam.id, prompt="Raíz cuadrada de 144:",
                        options=["10", "11", "12", "14"], answer="12",
                        skill="OA 3 - Números"),
    ])
    db.commit()
    st = models.Student(guardian_id=guard.id, level="MEDIA_1")
    db.add(st)
    db.add(models.Enrollment(student_id=st.id, course_id=course.id))
    db.commit()
db.close()
print("Seed listo. Usuarios: admin@aulasite.cl / profesor@demo.cl / apoderado@demo.cl (demo1234)")
