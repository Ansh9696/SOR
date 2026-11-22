# SOR

SOR (Security Orchestration and Response) is an early-stage project for exploring security event ingestion and monitoring workflows.

**Current status:** The repository contains a minimal FastAPI event-ingestion API. It accepts validated events, stores the latest events in process memory, and exposes basic health and retrieval endpoints. It is a learning/prototype foundation, not a production SOAR platform.

## Implemented in this version

- `POST /api/v1/events` — validate and ingest a security event.
- `GET /api/v1/events` — list recent events, with optional severity filtering and a bounded limit.
- `GET /api/v1/events/{event_id}` — retrieve an event by UUID.
- `GET /healthz` and `GET /readyz` — liveness and readiness checks.
- Pytest coverage for the API's initial behavior.
- Docker image, Compose configuration, a Kubernetes Deployment/Service example, and GitHub Actions CI.

### Important limitations

- Event data is held in memory and is lost when the process restarts.
- The API has no authentication or authorization. Do not expose it to untrusted networks.
- There are no integrations, alert correlation, workflow engine, or automated response actions yet.
- The Kubernetes manifest uses the placeholder image `sor-api:0.1.0`; build and make that image available to your cluster before deploying.
- No license has been added. Do not assume the code is licensed for reuse until one is selected.

## Run locally

Requires Python 3.12 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive API documentation is at `http://localhost:8000/docs`.

### Example: submit an event

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "endpoint-agent",
    "title": "Repeated failed login attempts",
    "description": "Five failed logins were observed for one account.",
    "severity": "high"
  }'
```

List recent events:

```bash
curl "http://localhost:8000/api/v1/events?severity=high&limit=20"
```

## Run tests

```bash
pytest -q
```

## Run with Docker Compose

```bash
docker compose up --build
```

The API listens on port 8000. The Compose service is configured with a read-only root filesystem, dropped Linux capabilities, and no-new-privileges. This is a local prototype setup, not a substitute for production hardening.

## Kubernetes example

Build the image and make it available to your cluster, then apply the manifests:

```bash
docker build -t sor-api:0.1.0 .
kubectl apply -f deploy/kubernetes/
```

The example uses one replica and an in-memory store. It is not suitable for durable or horizontally scaled workloads.

## Roadmap

1. Add durable event storage and database migrations.
2. Add authentication, authorization, and tenant boundaries before network exposure.
3. Add structured audit logging, metrics, and operational dashboards.
4. Define a stable event schema and versioning strategy.
5. Add integrations and alert triage workflows with tests.
6. Introduce response actions only with explicit authorization, safeguards, and audit trails.

These are planned areas of work, not existing features.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines. For substantial changes, open an issue to discuss the design first.

## Security

Do not commit credentials, tokens, private logs, or production data. See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.
