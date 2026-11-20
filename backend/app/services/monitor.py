import random
from datetime import datetime, timezone
SERVICES = {}
CHECKS = []
INCIDENTS = []
NEXT_SVC = [1]
NEXT_CHECK = [1]
def create_service(name, url, group="api", interval_seconds=60, alert_threshold_ms=1000, expected_status=200):
    sid = NEXT_SVC[0]; NEXT_SVC[0] += 1
    SERVICES[sid] = {"id": sid, "name": name, "url": url, "group": group, "interval_seconds": interval_seconds, "alert_threshold_ms": alert_threshold_ms, "expected_status": expected_status, "status": "unknown", "last_response_ms": None, "uptime": 100.0, "consecutive_failures": 0}
    return SERVICES[sid]
def check_service(sid, simulate=None):
    svc = SERVICES.get(sid)
    if not svc:
        return {"error": "service not found"}
    now = datetime.now(timezone.utc).isoformat()
    # Deterministic simulation by URL / simulate flag - no real external probing
    url = svc["url"].lower()
    mode = simulate or ("down" if "down" in url else "slow" if "slow" in url else "wrong-status" if "wrong" in url else "timeout" if "timeout" in url else "up")
    if mode == "down":
        status, code, ms = "down", 0, 0
    elif mode == "timeout":
        status, code, ms = "timeout", 0, 5000
    elif mode == "wrong-status":
        status, code, ms = "down", 500, 120
    elif mode == "slow":
        status, code, ms = "up", 200, 2400
    else:
        status, code, ms = "up", 200, random.randint(40, 180)
    is_up = status == "up" and code == svc["expected_status"]
    if not is_up:
        svc["consecutive_failures"] += 1
    else:
        svc["consecutive_failures"] = 0
    svc["status"] = "down" if not is_up else "up"
    svc["last_response_ms"] = ms
    alert = False
    reason = ""
    if not is_up:
        reason = f"Check failed: status={code}, mode={mode}"
        if svc["consecutive_failures"] >= 2:
            alert = True
            reason += " - ALERT: 2+ consecutive failures"
            if not any(i["service_id"] == sid and i["status"] == "open" for i in INCIDENTS):
                INCIDENTS.append({"id": len(INCIDENTS) + 1, "service_id": sid, "service_name": svc["name"], "started_at": now, "reason": reason, "status": "open"})
    elif ms > svc["alert_threshold_ms"]:
        alert = True
        reason = f"ALERT: Slow response {ms}ms > threshold {svc['alert_threshold_ms']}ms"
    cid = NEXT_CHECK[0]; NEXT_CHECK[0] += 1
    entry = {"id": cid, "service_id": sid, "service_name": svc["name"], "group": svc["group"], "timestamp": now, "status": "up" if is_up else "down", "http_status": code, "response_ms": ms, "alert": alert, "reason": reason}
    CHECKS.append(entry)
    # Update uptime
    svc_checks = [c for c in CHECKS if c["service_id"] == sid]
    svc["uptime"] = round(sum(1 for c in svc_checks if c["status"] == "up") / len(svc_checks) * 100, 1)
    return entry
def check_all():
    return [check_service(sid) for sid in list(SERVICES.keys())]
def dashboard():
    total = len(SERVICES)
    up = sum(1 for s in SERVICES.values() if s["status"] == "up")
    down = sum(1 for s in SERVICES.values() if s["status"] == "down")
    by_group = {}
    for s in SERVICES.values():
        by_group.setdefault(s["group"], {"total": 0, "up": 0, "down": 0})
        by_group[s["group"]]["total"] += 1
        by_group[s["group"]]["up" if s["status"] == "up" else "down" if s["status"] == "down" else "up"] += 0
        if s["status"] == "up":
            by_group[s["group"]]["up"] += 1
        elif s["status"] == "down":
            by_group[s["group"]]["down"] += 1
    avg_ms = round(sum(c["response_ms"] for c in CHECKS) / max(len(CHECKS), 1), 1)
    return {"total_services": total, "up": up, "down": down, "unknown": total - up - down, "total_checks": len(CHECKS), "avg_response_ms": avg_ms, "open_incidents": sum(1 for i in INCIDENTS if i["status"] == "open"), "by_group": by_group}
def seed():
    if SERVICES:
        return len(SERVICES)
    create_service("shop-api", "https://api.example.com/shop", "api", 60, 1000, 200)
    create_service("auth-api", "https://api.example.com/auth-down", "api", 60, 1000, 200)
    create_service("payment-api", "https://api.example.com/pay-slow", "payments", 60, 1000, 200)
    create_service("frontend", "https://example.com/", "web", 60, 1000, 200)
    return len(SERVICES)