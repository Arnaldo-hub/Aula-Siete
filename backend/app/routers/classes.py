from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role

router = APIRouter(prefix="/api", tags=["classes"])

class LiveClassIn(BaseModel):
    course_id: int
    lesson_id: int | None = None
    title: str
    starts_at: datetime
    ends_at: datetime

class RecordingIn(BaseModel):
    course_id: int
    title: str
    video_url: str
    live_class_id: int | None = None
    is_public: bool = False

class MaterialIn(BaseModel):
    course_id: int
    title: str
    file_url: str
    file_type: str | None = None
    lesson_id: int | None = None

def _jitsi_url(course_id: int, title: str) -> str:
    # Sala determinística por curso; en producción: Daily.co o Jitsi self-hosted
    slug = "".join(c if c.isalnum() else "-" for c in title.lower()).strip("-")
    return f"https://meet.jit.si/aulasite-c{course_id}-{slug}"

@router.post("/live-classes")
def schedule_live(data: LiveClassIn,
                  user: models.User = Depends(require_role("profesor", "admin")),
                  db: Session = Depends(get_db)):
    lc = models.LiveClass(course_id=data.course_id, lesson_id=data.lesson_id,
                          title=data.title, starts_at=data.starts_at,
                          ends_at=data.ends_at,
                          room_url=_jitsi_url(data.course_id, data.title))
    db.add(lc); db.commit(); db.refresh(lc)
    return {"id": lc.id, "room_url": lc.room_url}

@router.get("/live-classes")
def upcoming(db: Session = Depends(get_db)):
    rows = (db.query(models.LiveClass)
            .filter(models.LiveClass.starts_at >= datetime.utcnow())
            .order_by(models.LiveClass.starts_at).limit(50).all())
    return [{"id": r.id, "title": r.title, "course_id": r.course_id,
             "starts_at": r.starts_at.isoformat(), "room_url": r.room_url,
             "status": r.status} for r in rows]

@router.post("/recordings")
def upload_recording(data: RecordingIn,
                     user: models.User = Depends(require_role("profesor", "admin")),
                     db: Session = Depends(get_db)):
    r = models.Recording(course_id=data.course_id, title=data.title,
                         video_url=data.video_url,
                         live_class_id=data.live_class_id,
                         is_public=data.is_public)
    db.add(r); db.commit(); db.refresh(r)
    return {"id": r.id}

@router.get("/recordings")
def library(course_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Recording)
    if course_id:
        q = q.filter_by(course_id=course_id)
    return [{"id": r.id, "title": r.title, "video_url": r.video_url,
             "course_id": r.course_id} for r in q.order_by(
                 models.Recording.uploaded_at.desc()).all()]

@router.post("/materials")
def upload_material(data: MaterialIn,
                    user: models.User = Depends(require_role("profesor", "admin")),
                    db: Session = Depends(get_db)):
    m = models.Material(course_id=data.course_id, title=data.title,
                        file_url=data.file_url, file_type=data.file_type,
                        lesson_id=data.lesson_id)
    db.add(m); db.commit(); db.refresh(m)
    return {"id": m.id}

@router.get("/materials")
def materials(course_id: int, db: Session = Depends(get_db)):
    return [{"id": m.id, "title": m.title, "file_url": m.file_url,
             "file_type": m.file_type}
            for m in db.query(models.Material).filter_by(course_id=course_id).all()]
