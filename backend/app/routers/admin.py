from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..security import require_role
from ..bootstrap import run_seed, seed_banco_preguntas

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/reseed")
def reseed(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Recarga/verifica datos demo y el banco de preguntas. Solo administradores."""
    r1 = run_seed(db)
    r2 = seed_banco_preguntas(db)
    return {"ok": True, **r1, **r2}
