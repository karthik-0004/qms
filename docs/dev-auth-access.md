## Auth login works on any PC (local dev)

### Required idea

The frontend signs in via NextAuth Credentials, which calls:

- `AUTH_SERVICE_URL + /api/v1/auth/login`

So **every machine must point to the same running auth-service + database** (or at least a DB that contains the same user).

### Frontend setup

Create `frontend/apps/web/.env.local` (do not commit it) and set:

- `AUTH_SERVICE_URL="http://localhost:8001"` (when running `docker-compose.platform.yml`)
- `AUTH_SECRET` (any strong random value)

### Backend setup (local docker)

Start platform services:

- `docker-compose -f docker-compose.platform.yml up -d`

### Seed a super admin (optional)

Inside the `auth-service` container:

- Set env vars: `AUTH_SUPERADMIN_EMAIL`, `AUTH_SUPERADMIN_PASSWORD`
- Run: `python -m app.scripts.create_super_admin`

### Seed a tenant admin (recommended for dev)

1) Create a tenant (via `tenant-service`) and copy its UUID.

2) Inside the `auth-service` container set:

- `AUTH_TENANTADMIN_EMAIL`
- `AUTH_TENANTADMIN_PASSWORD`
- `AUTH_TENANTADMIN_TENANT_ID` (the tenant UUID)
- `AUTH_TENANTADMIN_ROLE` (usually `tenant_admin`)

3) Run one of:

- `python -m app.scripts.create_tenant_admin`
- `python -m app.scripts.seed_dev` (runs both super admin + tenant admin when env vars exist)

### Why you saw “Invalid email or password”

That UI toast is shown whenever sign-in fails. The most common causes are:

- `AUTH_SERVICE_URL` points to the wrong service/port
- You’re running a different DB (user doesn’t exist on this machine’s DB)
- The user exists but the password hash differs (seeded differently)

