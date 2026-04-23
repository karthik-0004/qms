# ──────────────────────────────────────────────────────────────
# Vault Agent sidecar configuration for Rainer Platform services
# Runs as a K8s init-container + sidecar to fetch and renew secrets.
# ──────────────────────────────────────────────────────────────

vault {
  address = "https://vault.rainer-infra.svc.cluster.local:8200"

  retry {
    num_retries = 5
  }
}

# Auto-auth using Kubernetes auth method
auto_auth {
  method "kubernetes" {
    mount_path = "auth/kubernetes"

    config = {
      role                 = "rainer-service"
      token_path           = "/var/run/secrets/kubernetes.io/serviceaccount/token"
      service_account_name = "${SERVICE_ACCOUNT_NAME}"
    }
  }

  sink "file" {
    config = {
      path = "/vault/token/.vault-token"
      mode = 0640
    }
  }
}

# Template: Database credentials
template {
  source      = "/vault/templates/db-credentials.ctmpl"
  destination = "/vault/secrets/db-credentials.env"
  perms       = "0640"

  exec {
    command = ["sh", "-c", "kill -HUP $(cat /tmp/app.pid) 2>/dev/null || true"]
  }
}

# Template: Redis credentials
template {
  source      = "/vault/templates/redis-credentials.ctmpl"
  destination = "/vault/secrets/redis-credentials.env"
  perms       = "0640"
}

# Template: Kafka credentials
template {
  source      = "/vault/templates/kafka-credentials.ctmpl"
  destination = "/vault/secrets/kafka-credentials.env"
  perms       = "0640"
}

# Template: JWT signing key
template {
  source      = "/vault/templates/jwt-secret.ctmpl"
  destination = "/vault/secrets/jwt-secret.env"
  perms       = "0640"
}
