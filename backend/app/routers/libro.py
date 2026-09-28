from datetime import date as date_t
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role

router = APIRouter(prefix="/api/libro", tags=["libro"])

def _owner(db: Session, cid: int, user) -> models.Classroom:
    c = db.get(models.Classroom, cid)
    if not c:
        raise HTTPException(404, "Curso no encontrado")
    if user.role != "admin" and c.teacher_id != user.id:
        raise HTTPException(403, "No es tu curso")
    return c

# ---- Cursos ----
class ClassroomIn(BaseModel):
    name: str
    level: str
    year: int
    school: str | None = None

@router.get("/classrooms")
def list_classrooms(user: models.User = Depends(require_role("profesor", "admin")),
                    db: Session = Depends(get_db)):
    q = db.query(models.Classroom)
    if user.role == "profesor":
        q = q.filter_by(teacher_id=user.id)
    return [{"id": c.id, "name": c.name, "level": c.level, "year": c.year,
             "school": c.school} for c in q.order_by(models.Classroom.id.desc()).all()]

@router.post("/classrooms")
def create_classroom(data: ClassroomIn,
                     user: models.User = Depends(require_role("profesor", "admin")),
                     db: Session = Depends(get_db)):
    c = models.Classroom(name=data.name, level=data.level, year=data.year,
                         school=data.school, teacher_id=user.id)
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id}

# ---- Alumnos del curso ----
class StudentsIn(BaseModel):
    names: list[str]   # una linea por alumno: "Nombre Apellido"

@router.get("/classrooms/{cid}/students")
def students(cid: int, user: models.User = Depends(require_role("profesor", "admin")),
             db: Session = Depends(get_db)):
    _owner(db, cid, user)
    rows = (db.query(models.ClassroomStudent)
            .filter_by(classroom_id=cid).order_by(models.ClassroomStudent.last_name).all())
    return [{"id": r.id, "name": f"{r.first_name} {r.last_name}"} for r in rows]

@router.post("/classrooms/{cid}/students")
def add_students(cid: int, data: StudentsIn,
                 user: models.User = Depends(require_role("profesor", "admin")),
                 db: Session = Depends(get_db)):
    _owner(db, cid, user)
    added = 0
    for line in data.names:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        first, last = parts[0], " ".join(parts[1:]) if len(parts) > 1 else ""
        db.add(models.ClassroomStudent(classroom_id=cid, first_name=first, last_name=last))
        added += 1
    db.commit()
    return {"added": added}

@router.delete("/students/{sid}")
def del_student(sid: int, user: models.User = Depends(require_role("profesor", "admin")),
                db: Session = Depends(get_db)):
    st = db.get(models.ClassroomStudent, sid)
    if not st:
        raise HTTPException(404, "Alumno no encontrado")
    _owner(db, st.classroom_id, user)
    db.delete(st); db.commit()
    return {"ok": True}

# ---- Asistencia ----
class AttSave(BaseModel):
    student_id: int
    date: str     # YYYY-MM-DD
    status: str   # P / A / R  ('' = borrar)

@router.get("/classrooms/{cid}/attendance")
def get_attendance(cid: int, month: str,   # YYYY-MM
                   user: models.User = Depends(require_role("profesor", "admin")),
                   db: Session = Depends(get_db)):
    _owner(db, cid, user)
    rows = (db.query(models.Attendance)
            .filter(models.Attendance.classroom_id == cid,
                    models.Attendance.date.like(f"{month}-%")).all())
    return [{"student_id": r.student_id, "date": str(r.date), "status": r.status} for r in rows]

@router.post("/classrooms/{cid}/attendance")
def save_attendance(cid: int, items: list[AttSave],
                    user: models.User = Depends(require_role("profesor", "admin")),
                    db: Session = Depends(get_db)):
    _owner(db, cid, user)
    for it in items:
        d = date_t.fromisoformat(it.date)
        row = (db.query(models.Attendance)
               .filter_by(classroom_id=cid, student_id=it.student_id, date=d).first())
        if it.status == "":
            if row:
                db.delete(row)
        elif row:
            row.status = it.status
        else:
            db.add(models.Attendance(classroom_id=cid, student_id=it.student_id,
                                     date=d, status=it.status))
    db.commit()
    return {"ok": True, "saved": len(items)}

# ---- Anotaciones de convivencia ----
class AnnIn(BaseModel):
    student_id: int
    date: str
    subject: str | None = None
    kind: str = "anotacion"
    text: str
    guardian_informed: bool = False

@router.get("/classrooms/{cid}/annotations")
def get_annotations(cid: int, student_id: int | None = None,
                    user: models.User = Depends(require_role("profesor", "admin")),
                    db: Session = Depends(get_db)):
    _owner(db, cid, user)
    q = db.query(models.Annotation).filter_by(classroom_id=cid)
    if student_id:
        q = q.filter_by(student_id=student_id)
    rows = q.order_by(models.Annotation.date.desc(), models.Annotation.id.desc()).limit(200).all()
    return [{"id": r.id, "student_id": r.student_id, "date": str(r.date),
             "subject": r.subject, "kind": r.kind, "text": r.text,
             "guardian_informed": r.guardian_informed} for r in rows]

@router.post("/classrooms/{cid}/annotations")
def add_annotation(cid: int, data: AnnIn,
                   user: models.User = Depends(require_role("profesor", "admin")),
                   db: Session = Depends(get_db)):
    _owner(db, cid, user)
    a = models.Annotation(classroom_id=cid, student_id=data.student_id,
                          date=date_t.fromisoformat(data.date), subject=data.subject,
                          kind=data.kind, text=data.text,
                          guardian_informed=data.guardian_informed)
    db.add(a); db.commit(); db.refresh(a)
    return {"id": a.id}

# ---- Planificación diaria (control de asignatura) ----
class PlanIn2(BaseModel):
    date: str
    block: str | None = None
    objective: str | None = None
    activity: str

@router.get("/classrooms/{cid}/plan")
def get_plan(cid: int, month: str | None = None,
             user: models.User = Depends(require_role("profesor", "admin")),
             db: Session = Depends(get_db)):
    _owner(db, cid, user)
    q = db.query(models.PlanEntry).filter_by(classroom_id=cid)
    if month:
        q = q.filter(models.PlanEntry.date.like(f"{month}-%"))
    rows = q.order_by(models.PlanEntry.date.desc(), models.PlanEntry.id.desc()).limit(200).all()
    return [{"id": r.id, "date": str(r.date), "block": r.block,
             "objective": r.objective, "activity": r.activity} for r in rows]

@router.post("/classrooms/{cid}/plan")
def add_plan(cid: int, data: PlanIn2,
             user: models.User = Depends(require_role("profesor", "admin")),
             db: Session = Depends(get_db)):
    _owner(db, cid, user)
    p = models.PlanEntry(classroom_id=cid, date=date_t.fromisoformat(data.date),
                         block=data.block, objective=data.objective, activity=data.activity)
    db.add(p); db.commit(); db.refresh(p)
    return {"id": p.id}

# ---- Notas ----
class GradeSave(BaseModel):
    student_id: int
    score: float | None

class EvalIn(BaseModel):
    subject: str
    title: str
    date: str
    max_score: float = 7.0

@router.post("/classrooms/{cid}/evaluations")
def create_eval(cid: int, data: EvalIn,
                user: models.User = Depends(require_role("profesor", "admin")),
                db: Session = Depends(get_db)):
    _owner(db, cid, user)
    d = date_t.fromisoformat(data.date)
    # una evaluacion = filas Grade vacias por alumno
    students_ = db.query(models.ClassroomStudent).filter_by(classroom_id=cid).all()
    for s in students_:
        db.add(models.Grade(classroom_id=cid, student_id=s.id, subject=data.subject,
                            title=data.title, gdate=d, max_score=data.max_score))
    db.commit()
    return {"ok": True, "students": len(students_)}

@router.get("/classrooms/{cid}/grades")
def get_grades(cid: int, subject: str | None = None,
               user: models.User = Depends(require_role("profesor", "admin")),
               db: Session = Depends(get_db)):
    _owner(db, cid, user)
    q = db.query(models.Grade).filter_by(classroom_id=cid)
    if subject:
        q = q.filter_by(subject=subject)
    rows = q.order_by(models.Grade.gdate.desc(), models.Grade.id).limit(500).all()
    return [{"id": r.id, "student_id": r.student_id, "subject": r.subject,
             "title": r.title, "score": float(r.score) if r.score is not None else None,
             "max_score": float(r.max_score), "date": str(r.gdate)} for r in rows]

@router.post("/grades/{gid}")
def save_grade(gid: int, data: GradeSave,
               user: models.User = Depends(require_role("profesor", "admin")),
               db: Session = Depends(get_db)):
    g = db.get(models.Grade, gid)
    if not g:
        raise HTTPException(404, "Nota no encontrada")
    _owner(db, g.classroom_id, user)
    g.score = data.score
    db.commit()
    return {"ok": True}

# ---- Reuniones de apoderados ----
class MeetingIn(BaseModel):
    date: str
    topic: str
    agreements: str | None = None

@router.get("/classrooms/{cid}/meetings")
def get_meetings(cid: int, user: models.User = Depends(require_role("profesor", "admin")),
                 db: Session = Depends(get_db)):
    _owner(db, cid, user)
    rows = (db.query(models.Meeting).filter_by(classroom_id=cid)
            .order_by(models.Meeting.date.desc()).all())
    return [{"id": r.id, "date": str(r.date), "topic": r.topic,
             "agreements": r.agreements} for r in rows]

@router.post("/classrooms/{cid}/meetings")
def add_meeting(cid: int, data: MeetingIn,
                user: models.User = Depends(require_role("profesor", "admin")),
                db: Session = Depends(get_db)):
    _owner(db, cid, user)
    m = models.Meeting(classroom_id=cid, date=date_t.fromisoformat(data.date),
                       topic=data.topic, agreements=data.agreements)
    db.add(m); db.commit(); db.refresh(m)
    return {"id": m.id}
