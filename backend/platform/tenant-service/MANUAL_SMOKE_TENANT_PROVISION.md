# Manual smoke checklist: tenant provision + welcome email

Use this after deploying migrations and configuring inter-service URLs (`auth`, `user`, `notification`) plus `PUBLIC_WEB_LOGIN_URL` / SMTP.

## Prerequisites

1. Master DB migrated (tenant profile columns + notification template + user-service system roles seed as applicable).
2. `tenant-service` can reach auth, user, and notification services on the URLs in its configuration.
3. SMTP for `notification-service` is valid for the target environment.

## Steps

1. Sign in as a **super_admin** and open **`/admin/tenants`**.
2. Choose **New tenant** and submit the full create form with a reachable **primary contact email** unique in `platform_users`.
3. Confirm **HTTP 201** and that the tenant appears in the list; open **`/admin/tenants/{slug}`** and verify workspace, primary contact, and profile snapshot.
4. Check the welcome inbox for **`tenant_admin_welcome`**: tenant name, login URL (`PUBLIC_WEB_LOGIN_URL`), temporary password present.
5. Log out and sign in **as that primary contact email** using the emailed password at the configured login URL; confirm tenant context loads.
6. Optional: intentionally break SMTP — tenant create should **still succeed** (`201`), with email failure surfaced only in tenant-service logs (not in API body).
