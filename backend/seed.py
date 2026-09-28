"""Poblado inicial: crea tablas (si no existen), datos demo y banco de preguntas Fase A."""
from app.database import SessionLocal, engine, Base, migrate
from app.bootstrap import run_seed, seed_banco_preguntas

migrate()
Base.metadata.create_all(bind=engine)
db = SessionLocal()
run_seed(db)
print("Banco Fase A:", seed_banco_preguntas(db))
db.close()
print("Seed listo. Usuarios: admin@aulasite.cl / profesor@demo.cl / apoderado@demo.cl (demo1234)")
