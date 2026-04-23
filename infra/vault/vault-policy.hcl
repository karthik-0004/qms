# ──────────────────────────────────────────────────────────────
# Vault policy for Rainer Platform services
# ──────────────────────────────────────────────────────────────

# Read database dynamic credentials
path "database/creds/rainer-service" {
  capabilities = ["read"]
}

# Read static KV secrets
path "secret/data/rainer/*" {
  capabilities = ["read"]
}

# Allow token renewal
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Allow looking up own token info
path "auth/token/lookup-self" {
  capabilities = ["read"]
}
