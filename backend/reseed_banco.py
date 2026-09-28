"""Carga el banco de preguntas Fase A (diagnosticos + PAES). Idempotente."""
from app.database import SessionLocal, Base, engine, migrate
from app.bootstrap import seed_banco_preguntas

migrate()
Base.metadata.create_all(bind=engine)
db = SessionLocal()
r = seed_banco_preguntas(db)
db.close()
print("Banco listo:", r)
