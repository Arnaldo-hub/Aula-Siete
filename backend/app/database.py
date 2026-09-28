from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

MIGRATIONS = [
    "ALTER TABLE questions ADD COLUMN IF NOT EXISTS difficulty INTEGER DEFAULT 2",
    "ALTER TABLE questions ADD COLUMN IF NOT EXISTS oa TEXT",
    "ALTER TABLE materials ADD COLUMN IF NOT EXISTS oa TEXT",
    "ALTER TABLE exams ADD COLUMN IF NOT EXISTS kind VARCHAR(20) DEFAULT 'simulacro'",
]

def migrate():
    """Aplica cambios de columnas en PostgreSQL sin borrar datos."""
    with engine.begin() as conn:
        for stmt in MIGRATIONS:
            try:
                conn.execute(text(stmt))
            except Exception:
                pass   # SQLite o columna ya existente: se ignora

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
