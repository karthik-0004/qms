# Platform services — URLs (local development)

Source of truth:
- `docker-compose.platform.yml` (platform-only stack)
- `docker-compose.yml` (full local dev stack)

## Public URLs (from your host machine)

All services are exposed on `localhost` when started with docker compose.

- **Gateway service**: `http://localhost:8000`
- **Auth service**: `http://localhost:8001`
- **Tenant service**: `http://localhost:8002`
- **User service**: `http://localhost:8003`
- **Audit service**: `http://localhost:8004`
- **Notification service**: `http://localhost:8005`
- **Config service**: `http://localhost:8006`
- **Workflow engine**: `http://localhost:8007`
- **Schedule service**: `http://localhost:8008`
- **File service**: `http://localhost:8009`
- **Reporting service**: `http://localhost:8010`
- **Analytics service**: `http://localhost:8011`

## Internal URLs (service-to-service, inside docker network)

Use these from other containers on the same compose network (e.g. `rainer-net`).

- **Gateway service**: `http://gateway-service:8000`
- **Auth service**: `http://auth-service:8001`
- **Tenant service**: `http://tenant-service:8002`
- **User service**: `http://user-service:8003`
- **Audit service**: `http://audit-service:8004`
- **Notification service**: `http://notification-service:8005`
- **Config service**: `http://config-service:8006`
- **Workflow engine**: `http://workflow-engine:8007`
- **Schedule service**: `http://schedule-service:8008`
- **File service**: `http://file-service:8009`
- **Reporting service**: `http://reporting-service:8010`
- **Analytics service**: `http://analytics-service:8011`

