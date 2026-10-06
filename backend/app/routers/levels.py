from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role

router = APIRouter(prefix="/api/levels", tags=["levels"])

# Asignaturas oficiales Mineduc para validacion por examenes libres
_BASICAS = ["Lenguaje y Comunicacion", "Matematica", "Ciencias Naturales",
            "Historia, Geografia y Cs. Sociales"]
_MEDIA = ["Lengua y Literatura", "Matematica", "Ciencias Naturales",
          "Historia, Geografia y Cs. Sociales", "Ingles"]

OFICIAL = {}
for _i in range(1, 7):
    OFICIAL[f"BASICA_{_i}"] = _BASICAS
for _i in range(7, 9):
    OFICIAL[f"BASICA_{_i}"] = _BASICAS + ["Ingles"]
for _i in range(1, 5):
    OFICIAL[f"MEDIA_{_i}"] = _MEDIA


class SeedIn(BaseModel):
    level: str
    teacher_id: int | None = None


@router.post("/seed")
def seed_level(data: SeedIn, user: models.User = Depends(require_role("admin")),
               db: Session = Depends(get_db)):
    """Crea las asignaturas y cursos oficiales de un nivel (1 click).
    Idempotente: no duplica si ya existen. Auto-inscribe alumnos del nivel."""
    subjects = OFICIAL.get(data.level)
    if not subjects:
        raise HTTPException(400, "Nivel no soportado. Use BASICA_1 a BASICA_8 o MEDIA_1 a MEDIA_4.")
    teacher = db.get(models.User, data.teacher_id) if data.teacher_id else None
    if data.teacher_id and (not teacher or teacher.role != "profesor"):
        raise HTTPException(400, "El docente seleccionado no existe o no es profesor.")
    created = 0
    course_ids = []
    for name in subjects:
        subj = db.query(models.Subject).filter_by(name=name, level=data.level).first()
        if not subj:
            subj = models.Subject(name=name, level=data.level)
            db.add(subj); db.commit(); db.refresh(subj)
        course = db.query(models.Course).filter_by(subject_id=subj.id, level=data.level).first()
        if not course:
            course = models.Course(subject_id=subj.id, level=data.level,
                                   teacher_id=teacher.id if teacher else None,
                                   title=f"{name} - {data.level}",
                                   description="Curso oficial de preparacion para examen libre (Mineduc)")
            db.add(course); db.commit(); db.refresh(course)
            created += 1
        elif teacher and not course.teacher_id:
            course.teacher_id = teacher.id
            db.commit()
        course_ids.append(course.id)
    enrolled = 0
    for st in db.query(models.Student).filter_by(level=data.level).all():
        for cid in course_ids:
            if not db.query(models.Enrollment).filter_by(student_id=st.id, course_id=cid).first():
                db.add(models.Enrollment(student_id=st.id, course_id=cid)); enrolled += 1
    db.commit()
    return {"level": data.level, "asignaturas": subjects,
            "cursos_nuevos": created, "cursos_total": len(course_ids),
            "docente": teacher.full_name if teacher else None,
            "alumnos_inscritos": enrolled}


def _level_label(lv):
    m = {"PREKINDER": "Prekinder", "KINDER": "Kinder"}
    for i in range(1, 9): m[f"BASICA_{i}"] = f"{i} Basico"
    for i in range(1, 5): m[f"MEDIA_{i}"] = f"{i} Medio"
    return m.get(lv, lv)


@router.get("/board")
def board(user: models.User = Depends(require_role("profesor", "admin")),
          db: Session = Depends(get_db)):
    """Tablero de relacion curso-docente-alumnos. Profesor ve solo lo suyo."""
    q = db.query(models.Course)
    if user.role == "profesor":
        q = q.filter_by(teacher_id=user.id)
    out = []
    for c in q.order_by(models.Course.id).all():
        subj = db.get(models.Subject, c.subject_id)
        teacher = db.get(models.User, c.teacher_id) if c.teacher_id else None
        studs = (db.query(models.Student, models.User)
                 .join(models.Enrollment, models.Enrollment.student_id == models.Student.id)
                 .filter(models.Enrollment.course_id == c.id)
                 .outerjoin(models.User, models.User.id == models.Student.user_id)
                 .order_by(models.Student.id).all())
        out.append({
            "course_id": c.id, "title": c.title,
            "subject": subj.name if subj else "-",
            "level": c.level, "level_label": _level_label(c.level),
            "teacher": teacher.full_name if teacher else "Sin asignar",
            "students": [{"id": s.id, "name": (u.full_name if u else f"Alumno #{s.id}"),
                          "level": _level_label(s.level)} for s, u in studs],
        })
    return out
