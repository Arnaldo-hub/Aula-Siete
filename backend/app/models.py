from sqlalchemy import (Column, BigInteger, String, Text, Date, DateTime, Integer,
                        Numeric, Boolean, ForeignKey, UniqueConstraint, JSON)
# JSON portable (funciona en SQLite y PostgreSQL)
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # admin|profesor|apoderado|alumno
    created_at = Column(DateTime(timezone=True), server_default="now()")

class Student(Base):
    __tablename__ = "students"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    guardian_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    run = Column(String, unique=True)
    birth_date = Column(Date)
    level = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="now()")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    level = Column(String, nullable=False)

class Course(Base):
    __tablename__ = "courses"
    id = Column(BigInteger, primary_key=True)
    subject_id = Column(BigInteger, ForeignKey("subjects.id"), nullable=False)
    level = Column(String, nullable=False)
    teacher_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)

class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id"),)
    id = Column(BigInteger, primary_key=True)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

class AcademicPlan(Base):
    __tablename__ = "academic_plans"
    id = Column(BigInteger, primary_key=True)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer)
    unit_title = Column(Text, nullable=False)
    objective = Column(Text)
    order_idx = Column(Integer, default=0)

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(BigInteger, primary_key=True)
    plan_id = Column(BigInteger, ForeignKey("academic_plans.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    content = Column(JSON, default=dict)
    order_idx = Column(Integer, default=0)

class LiveClass(Base):
    __tablename__ = "live_classes"
    id = Column(BigInteger, primary_key=True)
    course_id = Column(BigInteger, ForeignKey("courses.id"), nullable=False)
    lesson_id = Column(BigInteger, ForeignKey("lessons.id"))
    title = Column(Text, nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    room_url = Column(Text, nullable=False)
    status = Column(String, default="scheduled")

class Recording(Base):
    __tablename__ = "recordings"
    id = Column(BigInteger, primary_key=True)
    live_class_id = Column(BigInteger, ForeignKey("live_classes.id"))
    course_id = Column(BigInteger, ForeignKey("courses.id"), nullable=False)
    title = Column(Text, nullable=False)
    duration_sec = Column(Integer)
    video_url = Column(Text, nullable=False)
    is_public = Column(Boolean, default=False)
    uploaded_at = Column(DateTime(timezone=True), server_default="now()")

class Material(Base):
    __tablename__ = "materials"
    id = Column(BigInteger, primary_key=True)
    course_id = Column(BigInteger, ForeignKey("courses.id"), nullable=False)
    lesson_id = Column(BigInteger, ForeignKey("lessons.id"))
    title = Column(Text, nullable=False)
    file_url = Column(Text, nullable=False)
    file_type = Column(String)

class Exam(Base):
    __tablename__ = "exams"
    id = Column(BigInteger, primary_key=True)
    subject_id = Column(BigInteger, ForeignKey("subjects.id"), nullable=False)
    level = Column(String, nullable=False)
    title = Column(Text, nullable=False)
    time_limit_min = Column(Integer, default=90)
    is_simulation = Column(Boolean, default=True)

class Question(Base):
    __tablename__ = "questions"
    id = Column(BigInteger, primary_key=True)
    exam_id = Column(BigInteger, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    prompt = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    answer = Column(String, nullable=False)
    skill = Column(String)
    order_idx = Column(Integer, default=0)

class ExamAttempt(Base):
    __tablename__ = "exam_attempts"
    id = Column(BigInteger, primary_key=True)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    exam_id = Column(BigInteger, ForeignKey("exams.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default="now()")
    finished_at = Column(DateTime(timezone=True))
    score = Column(Numeric(5, 2))
    answers = Column(JSON, default=dict)

class Progress(Base):
    __tablename__ = "progress"
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    lesson_id = Column(BigInteger, ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True)
    status = Column(String, default="pending")
    updated_at = Column(DateTime(timezone=True), server_default="now()")

class Doubt(Base):
    __tablename__ = "doubts"
    id = Column(BigInteger, primary_key=True)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    asked_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default="now()")
    answered_at = Column(DateTime(timezone=True))

# ===== Libro de Clases Digital =====
class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)            # ej: "4 Básico B"
    level = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    school = Column(Text)
    teacher_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

class ClassroomStudent(Base):
    __tablename__ = "classroom_students"
    id = Column(BigInteger, primary_key=True)
    classroom_id = Column(BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("classroom_id", "student_id", "date"),)
    id = Column(BigInteger, primary_key=True)
    classroom_id = Column(BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("classroom_students.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(1), nullable=False, default="P")   # P / A / R

class Annotation(Base):
    __tablename__ = "annotations"
    id = Column(BigInteger, primary_key=True)
    classroom_id = Column(BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("classroom_students.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    subject = Column(Text)
    kind = Column(String(12), default="anotacion")  # positiva / negativa / entrevista
    text = Column(Text, nullable=False)
    guardian_informed = Column(Boolean, default=False)

class PlanEntry(Base):
    __tablename__ = "plan_entries"
    id = Column(BigInteger, primary_key=True)
    classroom_id = Column(BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    block = Column(Text)                 # ej: "1ª hora"
    objective = Column(Text)             # OA / OAT
    activity = Column(Text)

class Grade(Base):
    __tablename__ = "grades"
    id = Column(BigInteger, primary_key=True)
    classroom_id = Column(BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(BigInteger, ForeignKey("classroom_students.id", ondelete="CASCADE"), nullable=False)
    subject = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    score = Column(Numeric(5, 2))
    max_score = Column(Numeric(5, 2), default=7.0)
    gdate = Column(Date, nullable=False)

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(BigInteger, primary_key=True)
    classroom_id = Column(BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    topic = Column(Text, nullable=False)
    agreements = Column(Text)
