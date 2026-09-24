"""Poblado inicial: crea tablas (si no existen) y datos demo."""
from app.database import SessionLocal, engine, Base
from app.bootstrap import run_seed

Base.metadata.create_all(bind=engine)
db = SessionLocal()
run_seed(db)
db.close()
print("Seed listo. Usuarios: admin@aulasite.cl / profesor@demo.cl / apoderado@demo.cl (demo1234)")
