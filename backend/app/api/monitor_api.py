from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.monitor import SERVICES, CHECKS, INCIDENTS, create_service, check_service, check_all, dashboard, seed
router = APIRouter()
class SvcIn(BaseModel):
    name: str
    url: str
    group: str = "api"
    interval_seconds: int = 60
    alert_threshold_ms: int = 1000
    expected_status: int = 200
@router.post("/services")
def add_svc(body: SvcIn):
    return create_service(body.name, body.url, body.group, body.interval_seconds, body.alert_threshold_ms, body.expected_status)
@router.get("/services")
def list_svcs(group: str = ""):
    items = list(SERVICES.values())
    if group:
        items = [s for s in items if s["group"] == group]
    return {"total": len(items), "services": items}
@router.get("/services/{sid}")
def get_svc(sid: int):
    return SERVICES.get(sid, {"error": "not found"})
@router.post("/services/{sid}/check")
def check_one(sid: int, simulate: Optional[str] = None):
    return check_service(sid, simulate)
@router.post("/check-all")
def check_all_route():
    return {"checked": len(check_all()), "results": check_all() if False else []}
@router.get("/checks")
def list_checks(service_id: int = 0, status: str = ""):
    items = CHECKS
    if service_id:
        items = [c for c in items if c["service_id"] == service_id]
    if status:
        items = [c for c in items if c["status"] == status]
    return {"total": len(items), "checks": items}
@router.get("/incidents")
def incidents():
    return {"total": len(INCIDENTS), "incidents": INCIDENTS}
@router.post("/seed")
def do_seed():
    return {"seeded": seed()}
@router.get("/dashboard")
def dash():
    return dashboard()