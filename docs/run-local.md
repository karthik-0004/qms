## Local Development (Backend)

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- Node.js 20+

### Start infrastructure (DB, Redis, Kafka, MinIO, etc.)

```bash
make up-infra
```

### (Optional) Start observability (Grafana, Jaeger, Prometheus)

```bash
make up-observability
```

### Install dependencies

```bash
make install-dev
make install-frontend
```

### Run migrations

```bash
make migrate-master
```

### Start platform backend services (Phase A)

```bash
docker-compose up auth-service tenant-service user-service audit-service
```

### Swagger docs (local)
- auth-service: `http://localhost:8001/docs`
- tenant-service: `http://localhost:8002/docs`
- user-service: `http://localhost:8003/docs`
- audit-service: `http://localhost:8004/docs`

### Next.js on the host + gateway on the host (Windows / hybrid)

The web app rewrites `/api/platform/*` to the gateway (`NEXT_PUBLIC_API_URL`, default `http://localhost:8000`). The gateway then calls **tenant-service** using `TENANT_SERVICE_URL`.

- **Symptom**: JSON `UPSTREAM_UNREACHABLE` / “No address associated with hostname” when opening tenant APIs — the gateway is trying a **Docker-only** hostname (e.g. `tenant-service`) from a process running on Windows outside the compose network.
- **Fix**: In `backend/platform/gateway-service/.env` (copy from `.env.example` there), set:

  `TENANT_SERVICE_URL=http://localhost:8002`

  Use the same pattern for other upstreams you run as local processes (`http://localhost:<port>`), not `http://<service-name>:<port>`, unless you are inside Docker.

- **Start tenant-service** (port **8002**): from repo root, after infra + migrations per above:

  `docker compose up -d tenant-service`

  Or run it with `uvicorn` from `backend/platform/tenant-service` using that service’s `.env.example`.

- **Verify**:
  - `curl -sS "http://localhost:8002/health/live"`
  - `curl -sS "http://localhost:8000/api/v1/tenants?page=1&page_size=1"` (with any required auth headers your gateway expects)
  - In the browser: `http://localhost:3000/api/platform/tenants?page=1&page_size=10`

