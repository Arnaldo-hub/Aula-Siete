from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..security import require_role
from ..bootstrap import run_seed

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/reseed")
def reseed(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """Recarga/verifica los datos demo. Solo administradores."""
    return run_seed(db)
