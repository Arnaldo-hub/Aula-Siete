import unicodedata
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role

router = APIRouter(prefix="/api/levels", tags=["levels"])

# Asignaturas oficiales Mineduc para validacion por examenes libres (con tildes)
_BASICAS = ["Lenguaje y Comunicación", "Matemática", "Ciencias Naturales",
            "Historia, Geografía y Cs. Sociales"]
_MEDIA = ["Lengua y Literatura", "Matemática", "Ciencias Naturales",
          "Historia, Geografía y Cs. Sociales", "Inglés"]

LEVEL_LABELS = {}
for _i in range(1, 9):
    LEVEL_LABELS[f"BASICA_{_i}"] = f"{_i}° Básico"
for _i in range(1, 5):
    LEVEL_LABELS[f"MEDIA_{_i}"] = f"{_i}° Medio"

OFICIAL = {}
for _i in range(1, 7):
    OFICIAL[f"BASICA_{_i}"] = _BASICAS
for _i in range(7, 9):
    OFICIAL[f"BASICA_{_i}"] = _BASICAS + ["Inglés"]
for _i in range(1, 5):
    OFICIAL[f"MEDIA_{_i}"] = _MEDIA


def _norm(s: str) -> str:
    """Compara sin tildes ni mayusculas (para no duplicar asignaturas viejas)."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def _find_subject(db: Session, name: str, level: str):
    for s in db.query(models.Subject).filter_by(level=level).all():
        if _norm(s.name) == _norm(name):
            return s
    return None


def _pretty_title(name: str, level: str) -> str:
    return f"{name} — {LEVEL_LABELS.get(level, level)}"


def _ensure_course(db: Session, name: str, level: str, teacher) -> tuple:
    """Busca o crea la asignatura y el curso; arregla tildes y titulo si estan viejos."""
    subj = _find_subject(db, name, level)
    if not subj:
        subj = models.Subject(name=name, level=level)
        db.add(subj); db.commit(); db.refresh(subj)
    elif subj.name != name:
        subj.name = name
        db.commit()
    course = db.query(models.Course).filter_by(subject_id=subj.id, level=level).first()
    created = False
    if not course:
        course = models.Course(subject_id=subj.id, level=level,
                               teacher_id=teacher.id if teacher else None,
                               title=_pretty_title(name, level),
                               description="Curso oficial de preparación para examen libre (Mineduc)")
        db.add(course); db.commit(); db.refresh(course)
        created = True
    else:
        if teacher and not course.teacher_id:
            course.teacher_id = teacher.id
        if course.title != _pretty_title(name, level):
            course.title = _pretty_title(name, level)
        db.commit()
    return course, created


def _auto_enroll(db: Session, level: str, course_ids: list) -> int:
    enrolled = 0
    for st in db.query(models.Student).filter_by(level=level).all():
        for cid in course_ids:
            if not db.query(models.Enrollment).filter_by(student_id=st.id, course_id=cid).first():
                db.add(models.Enrollment(student_id=st.id, course_id=cid)); enrolled += 1
    db.commit()
    return enrolled


class SeedIn(BaseModel):
    level: str
    teacher_id: int | None = None


@router.post("/seed")
def seed_level(data: SeedIn, user: models.User = Depends(require_role("admin")),
               db: Session = Depends(get_db)):
    """Crea TODAS las asignaturas oficiales del nivel (1 click).
    Idempotente: no duplica y arregla nombres/titulos viejos."""
    subjects = OFICIAL.get(data.level)
    if not subjects:
        raise HTTPException(400, "Nivel no soportado. Use BASICA_1 a BASICA_8 o MEDIA_1 a MEDIA_4.")
    teacher = db.get(models.User, data.teacher_id) if data.teacher_id else None
    if data.teacher_id and (not teacher or teacher.role != "profesor"):
        raise HTTPException(400, "El docente seleccionado no existe o no es profesor.")
    created = 0
    ids = []
    for name in subjects:
        course, was_created = _ensure_course(db, name, data.level, teacher)
        created += 1 if was_created else 0
        ids.append(course.id)
    enrolled = _auto_enroll(db, data.level, ids)
    return {"level": data.level, "nivel": LEVEL_LABELS[data.level],
            "asignaturas": subjects, "cursos_nuevos": created, "cursos_total": len(ids),
            "docente": teacher.full_name if teacher else None,
            "alumnos_inscritos": enrolled}


class SingleIn(BaseModel):
    name: str
    level: str
    teacher_id: int | None = None


@router.post("/subject")
def create_single(data: SingleIn, user: models.User = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    """Crea UNA asignatura/curso suelta para un nivel."""
    if data.level not in LEVEL_LABELS:
        raise HTTPException(400, "Nivel no soportado.")
    teacher = db.get(models.User, data.teacher_id) if data.teacher_id else None
    if data.teacher_id and (not teacher or teacher.role != "profesor"):
        raise HTTPException(400, "El docente seleccionado no existe o no es profesor.")
    course, created = _ensure_course(db, data.name.strip(), data.level, teacher)
    enrolled = _auto_enroll(db, data.level, [course.id])
    return {"curso": course.title, "nuevo": created,
            "docente": teacher.full_name if teacher else None,
            "alumnos_inscritos": enrolled}


@router.get("/board")
def board(user: models.User = Depends(require_role("profesor", "admin")),
          db: Session = Depends(get_db)):
    """Tablero curso-docente-alumnos. Profesor ve solo lo suyo."""
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
            "level": c.level, "level_label": LEVEL_LABELS.get(c.level, c.level),
            "teacher": teacher.full_name if teacher else "Sin asignar",
            "students": [{"id": s.id, "name": (u.full_name if u else f"Alumno #{s.id}"),
                          "level": LEVEL_LABELS.get(s.level, s.level)} for s, u in studs],
        })
    return out
