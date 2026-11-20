from app.services.monitor import create_service, check_service, dashboard
def test_up_service():
    s = create_service("up-svc", "https://example.com/up", "api", 60, 1000, 200)
    c = check_service(s["id"], "up")
    assert c["status"] == "up" and c["http_status"] == 200
def test_down_detection():
    s = create_service("down-svc", "https://example.com/down", "api", 60, 1000, 200)
    c = check_service(s["id"], "down")
    assert c["status"] == "down" and c["http_status"] == 0
def test_timeout():
    s = create_service("to-svc", "https://example.com/timeout", "api", 60, 1000, 200)
    c = check_service(s["id"], "timeout")
    assert c["status"] == "down" and c["response_ms"] == 5000
def test_wrong_status():
    s = create_service("wrong-svc", "https://example.com/wrong", "api", 60, 1000, 200)
    c = check_service(s["id"], "wrong-status")
    assert c["http_status"] == 500 and c["status"] == "down"
def test_slow_alert():
    s = create_service("slow-svc", "https://example.com/slow", "api", 60, 1000, 200)
    c = check_service(s["id"], "slow")
    assert c["response_ms"] > 1000 and c["alert"] is True