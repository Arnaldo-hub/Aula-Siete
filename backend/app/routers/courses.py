from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import get_current_user, require_role

router = APIRouter(prefix="/api", tags=["courses"])

class CourseIn(BaseModel):
    subject_id: int
    level: str
    title: str
    description: str | None = None

class PlanIn(BaseModel):
    year: int
    month: int | None = None
    unit_title: str
    objective: str | None = None

class LessonIn(BaseModel):
    plan_id: int
    title: str
    date: str
    content: dict = {}

# ---- Catálogos ----
@router.get("/subjects")
def list_subjects(db: Session = Depends(get_db)):
    return [{"id": s.id, "name": s.name, "level": s.level}
            for s in db.query(models.Subject).all()]

@router.get("/levels")
def list_levels():
    return ["PREKINDER", "KINDER", "BASICA_1", "BASICA_2", "BASICA_3", "BASICA_4",
            "BASICA_5", "BASICA_6", "BASICA_7", "BASICA_8",
            "MEDIA_1", "MEDIA_2", "MEDIA_3", "MEDIA_4"]

@router.get("/courses")
def list_courses(level: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Course)
    if level:
        q = q.filter_by(level=level)
    return [{"id": c.id, "title": c.title, "level": c.level,
             "description": c.description} for c in q.all()]

# ---- Panel del profesor: mis cursos + alumnos ----
@router.get("/my/courses")
def my_courses(user: models.User = Depends(require_role("profesor", "admin")),
               db: Session = Depends(get_db)):
    rows = (db.query(models.Course)
            .filter(models.Course.teacher_id == user.id)
            .order_by(models.Course.id.desc()).all())
    out = []
    for c in rows:
        count = db.query(models.Enrollment).filter_by(course_id=c.id).count()
        subj = db.get(models.Subject, c.subject_id)
        out.append({"id": c.id, "title": c.title, "level": c.level,
                    "description": c.description, "students": count,
                    "subject": subj.name if subj else ""})
    return out

@router.get("/courses/{course_id}/students")
def course_students(course_id: int,
                    user: models.User = Depends(require_role("profesor", "admin")),
                    db: Session = Depends(get_db)):
    c = db.get(models.Course, course_id)
    if not c:
        raise HTTPException(404, "Curso no encontrado")
    if user.role == "profesor" and c.teacher_id != user.id:
        raise HTTPException(403, "No es tu curso")
    rows = (db.query(models.Student)
            .join(models.Enrollment, models.Enrollment.student_id == models.Student.id)
            .filter(models.Enrollment.course_id == course_id).all())
    return [{"id": s.id, "level": s.level} for s in rows]

# ---- Creación ----
@router.post("/courses")
def create_course(data: CourseIn,
                  user: models.User = Depends(require_role("profesor", "admin")),
                  db: Session = Depends(get_db)):
    c = models.Course(subject_id=data.subject_id, level=data.level,
                      teacher_id=user.id, title=data.title,
                      description=data.description)
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id}

@router.post("/enroll")
def enroll(student_id: int, course_id: int,
           user: models.User = Depends(require_role("apoderado", "admin")),
           db: Session = Depends(get_db)):
    if user.role == "apoderado":
        st = db.get(models.Student, student_id)
        if not st or st.guardian_id != user.id:
            raise HTTPException(403, "No autorizado")
    if db.query(models.Enrollment).filter_by(student_id=student_id,
                                             course_id=course_id).first():
        raise HTTPException(409, "Ya inscrito")
    db.add(models.Enrollment(student_id=student_id, course_id=course_id))
    db.commit()
    return {"ok": True}

# ---- Planificación académica ----
@router.post("/plans")
def create_plan(data: PlanIn, course_id: int,
                user: models.User = Depends(require_role("profesor", "admin")),
                db: Session = Depends(get_db)):
    p = models.AcademicPlan(course_id=course_id, year=data.year,
                            month=data.month, unit_title=data.unit_title,
                            objective=data.objective)
    db.add(p); db.commit(); db.refresh(p)
    return {"id": p.id}

@router.post("/lessons")
def create_lesson(data: LessonIn,
                  user: models.User = Depends(require_role("profesor", "admin")),
                  db: Session = Depends(get_db)):
    l = models.Lesson(plan_id=data.plan_id, title=data.title,
                      date=data.date, content=data.content)
    db.add(l); db.commit(); db.refresh(l)
    return {"id": l.id}

@router.get("/courses/{course_id}/plan")
def course_plan(course_id: int, db: Session = Depends(get_db)):
    plans = (db.query(models.AcademicPlan)
             .filter_by(course_id=course_id).order_by(models.AcademicPlan.order_idx).all())
    out = []
    for p in plans:
        lessons = (db.query(models.Lesson)
                   .filter_by(plan_id=p.id).order_by(models.Lesson.date).all())
        out.append({"id": p.id, "unit": p.unit_title, "month": p.month,
                    "objective": p.objective,
                    "lessons": [{"id": l.id, "title": l.title, "date": str(l.date)}
                                for l in lessons]})
    return out
