# Environment reference (RainerQMS / Rainer platform)

This file summarizes **non-secret** environment variables used across the repo. **`.env.example` files use explicit placeholders** (`CHANGE_ME_IN_PRODUCTION`, `CHANGE_ME_DB_PASSWORD`, `YOUR_JWT_SECRET_MIN_32_CHARS_CHANGE_ME`, etc.); copy values from your real secrets manager in each environment. `docker-compose.yml` still embeds **local-only** dev credentials so the stack can start without a prior `.env` — do not treat those as production defaults.

## Conventions

| Pattern | Meaning |
|--------|---------|
| `NEXT_PUBLIC_*` | Exposed to the browser at build time (Next.js). |
| `*_URL` | HTTP base URL for a service (no trailing `/api/v1` unless noted). |
| Docker DNS | Hostnames like `auth-service` resolve **only** inside the Compose network. |

## Placeholders in `.env.example` (Phase 9 audit)

| Placeholder | Typical use |
|-------------|-------------|
| `CHANGE_ME_DB_PASSWORD` | PostgreSQL password segment in `DATABASE_URL` / `POSTGRES_ADMIN_URL`. Must match your database instance (for Compose dev, align with `POSTGRES_PASSWORD` in `docker-compose.yml`). |
| `CHANGE_ME_IN_PRODUCTION` | `RAINER_MASTER_SECRET`, bootstrap passwords, and similar high-impact secrets. |
| `YOUR_JWT_SECRET_MIN_32_CHARS_CHANGE_ME` | `JWT_SECRET_KEY` (HS256 signing); use a long random string in every non-local environment. |
| `CHANGE_ME_REDIS_PASSWORD` | Redis password in `REDIS_URL` (Compose uses a fixed dev password; mirror it locally or set your own). |
| `CHANGE_ME_MINIO_SECRET` | S3/MinIO secret key. |
| `CHANGE_ME_NEXTAUTH_SECRET` | Next.js / Auth.js cookie encryption (`AUTH_SECRET` / `NEXTAUTH_SECRET`). |

## Platform gateway (`backend/platform/gateway-service`)

| Variable | Example (local host) | Notes |
|----------|----------------------|--------|
| `PORT` | `8000` | Gateway listen port. |
| `AUTH_SERVICE_URL` | `http://localhost:8001` | Use Docker name `http://auth-service:8001` inside Compose. |
| `TENANT_SERVICE_URL` | `http://localhost:8002` | |
| `DOCUMENT_SERVICE_URL` | `http://localhost:8020` | QMS document-service. |
| `QUALITY_EVENT_SERVICE_URL` | `http://localhost:8021` | |
| `CAPA_SERVICE_URL` | `http://localhost:8022` | |
| `TRAINING_SERVICE_URL` | `http://localhost:8023` | |
| `EQUIPMENT_SERVICE_URL` | `http://localhost:8024` | |
| `ANALYTICS_SERVICE_URL` | `http://localhost:8011` | |
| `JWT_SECRET_KEY` | See placeholder table | Must match auth-service and other token issuers. |
| `RAINER_MASTER_SECRET` | See placeholder table | Inter-service trust / signing. |
| `REDIS_URL` | `redis://localhost:6379/0` | Often includes password in Docker (`CHANGE_ME_REDIS_PASSWORD` in examples). |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated browser origins. |

Compose `gateway-service` environment sets the above using **service hostnames** (`document-service`, `quality-event-service`, `capa-service`, `training-service`, `equipment-service`, `analytics-service`, CCV services on `8040`–`8044`, etc.) — verified against `docker-compose.yml` service names.

## Web app (`frontend/apps/web`)

| Variable | Example | Notes |
|----------|---------|--------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | **Browser** must reach the gateway (host port map). Do **not** set this to `http://gateway-service:8000` in client-visible env — that hostname exists only inside Docker. |
| `NEXT_PUBLIC_QMS_API_URL` | `http://localhost:8000` | Prefer gateway for all QMS clients. |
| `NEXT_PUBLIC_QMS_*_API_URL` | *(optional)* | Per-service overrides only for debugging. |
| `AUTH_SERVICE_URL` | `http://localhost:8001` | Server-side NextAuth / credentials provider. In Compose, `http://auth-service:8001` is correct for the **web container**. |
| `AUTH_SECRET` / `NEXTAUTH_SECRET` | Placeholder in `.env.example` | Required for session/crypto. |

## Docker Compose

- Compose injects internal URLs (`http://*-service:*`) for services running **in** the network.
- The `web` service build args / runtime `NEXT_PUBLIC_*` must stay **host-reachable** (usually `http://localhost:8000`) so the browser hits the published gateway port, not an internal-only DNS name.
- EM/CCV services use `redis://:rainer_redis_dev@redis:6379/0` and `kafka:29092` for in-network Redis and Kafka (aligned with the `kafka` service listener).

## Kafka / async (training notifications)

- Training bulk notifications after document approval may use Kafka in a future iteration; until then the UI may call assignment APIs directly. Search code for `Kafka` / `TODO` in training flows.

## MinIO / S3

- Used by reporting and file flows; see `docker-compose.yml` and per-service `.env.example` for `S3_*` and `MINIO_*` placeholders.
