import os
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import require_role, guardian_of

router = APIRouter(prefix="/api/payments", tags=["payments"])

PLANS = {
    "grupal": {"name": "Plan Grupo En Vivo - Aula Siete", "amount": 49900},
    "uno_a_uno": {"name": "Plan Intensivo 1 a 1 - Aula Siete", "amount": 119900},
}

def _sdk():
    token = os.getenv("MP_ACCESS_TOKEN", "")
    if not token:
        raise HTTPException(503, "Pagos no configurados: falta MP_ACCESS_TOKEN en Render (Environment)")
    import mercadopago
    return mercadopago.SDK(token)

@router.get("/plans")
def plans():
    return [{"id": k, "name": v["name"], "amount": v["amount"],
             "formatted": f"${v['amount']:,}".replace(",", ".") + " CLP/mes"} for k, v in PLANS.items()]

@router.post("/subscribe")
def subscribe(plan: str, student_id: int,
              user: models.User = Depends(require_role("apoderado", "admin")),
              db: Session = Depends(get_db)):
    if plan not in PLANS:
        raise HTTPException(400, "Plan inválido")
    if user.role == "apoderado":
        guardian_of(student_id, user, db)
    base = os.getenv("PUBLIC_BASE_URL", "https://aulasiete.cl")
    r = _sdk().preapproval().create({
        "reason": PLANS[plan]["name"],
        "external_reference": str(student_id),
        "payer_email": user.email,
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": PLANS[plan]["amount"],
            "currency_id": "CLP",
        },
        "back_url": f"{base}/app/suscripcion?estado=ok",
        "status": "pending",
    })
    if r["status"] not in (200, 201):
        raise HTTPException(502, f"Mercado Pago rechazó la suscripción: {r.get('response')}")
    resp = r["response"]
    sub = models.Subscription(student_id=student_id, guardian_id=user.id, plan=plan,
                              amount=PLANS[plan]["amount"],
                              mp_preapproval_id=str(resp["id"]), status="pending")
    db.add(sub); db.commit(); db.refresh(sub)
    return {"init_point": resp["init_point"], "preapproval_id": resp["id"], "subscription_id": sub.id}

@router.get("/status")
def status(student_id: int,
           user: models.User = Depends(require_role("apoderado", "admin")),
           db: Session = Depends(get_db)):
    if user.role == "apoderado":
        guardian_of(student_id, user, db)
    subs = (db.query(models.Subscription).filter_by(student_id=student_id)
            .order_by(models.Subscription.id.desc()).all())
    return [{"id": s.id, "plan": s.plan, "amount": float(s.amount), "status": s.status,
             "date": str(s.created_at)[:10]} for s in subs]

@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    """Mercado Pago notifica aquí los cambios de la suscripción."""
    body = await request.json()
    pre_id = (body.get("data") or {}).get("id")
    if not pre_id:
        return {"ok": True}
    try:
        info = _sdk().preapproval().get(str(pre_id)).get("response", {})
    except Exception:
        return {"ok": True}
    sub = db.query(models.Subscription).filter_by(mp_preapproval_id=str(pre_id)).first()
    if sub:
        sub.status = info.get("status", sub.status)
        db.commit()
    return {"ok": True}
