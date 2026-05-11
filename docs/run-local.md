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

