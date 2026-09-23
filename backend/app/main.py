from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth, users, courses, classes, exams, reports

app = FastAPI(title="Aula Site API",
              description="Plataforma de apoyo pedagógico para Exámenes Libres (Chile)",
              version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth.router, users.router, courses.router,
          classes.router, exams.router, reports.router):
    app.include_router(r)

@app.get("/health")
def health():
    return {"status": "ok"}
