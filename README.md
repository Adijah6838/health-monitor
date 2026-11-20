# Network Service Health Monitoring Platform
Simulated monitoring. Register services, run health checks, measure response time, availability history, alert thresholds, failure detection, grouping, dashboard, incidents, schedules.
## Safety
Simulated checks - no real external probing. Outcomes deterministic by URL pattern / simulate flag.
## Run Backend (Terminal 1)
cd backend; uvicorn app.main:app --port 8011 --reload
## Run Frontend (Terminal 2)
cd frontend; npm run dev
# http://localhost:5173/
## Test
cd backend; python -m pytest tests -v
## Endpoints
- POST /api/services {name, url, group, interval_seconds, alert_threshold_ms, expected_status}
- GET /api/services?group=
- POST /api/services/{id}/check?simulate=
- POST /api/check-all
- GET /api/checks?service_id=&status=
- GET /api/incidents
- POST /api/seed
- GET /api/dashboard
## Simulation
- URL contains 'down' -> down, status 0
- 'slow' -> up, 2400ms, slow alert
- 'wrong' -> HTTP 500, down
- 'timeout' -> 5000ms, down
- Incident opens after 2 consecutive failures