#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ ! -f "$REPO_ROOT/docker-compose.infra.yml" ]; then
  echo "Error: docker-compose.infra.yml not found in $REPO_ROOT"
  exit 1
fi

STACK="${1:-qms}"
TIMEOUT="${2:-180}"

case "$STACK" in
  platform)
    FILES="-f $REPO_ROOT/docker-compose.platform.yml"
    ;;
  qms)
    FILES="-f $REPO_ROOT/docker-compose.qms.yml"
    ;;
  em)
    FILES="-f $REPO_ROOT/docker-compose.em.yml"
    ;;
  ccv)
    FILES="-f $REPO_ROOT/docker-compose.ccv.yml"
    ;;
  all)
    FILES="-f $REPO_ROOT/docker-compose.platform.yml"
    ALL_EXTRA=1
    ;;
  *)
    echo "Usage: $0 {platform|qms|em|ccv|all}"
    exit 1
    ;;
esac

echo "Starting infrastructure..."
docker compose -f "$REPO_ROOT/docker-compose.infra.yml" -p rainerinfra up -d

echo "Starting $STACK services..."
docker compose $FILES up -d

if [ -n "${ALL_EXTRA:-}" ]; then
  echo "Starting remaining domains..."
  docker compose -f "$REPO_ROOT/docker-compose.qms.yml" -p rainerqms up -d
  docker compose -f "$REPO_ROOT/docker-compose.em.yml" -p rainerem up -d
  docker compose -f "$REPO_ROOT/docker-compose.ccv.yml" -p rainerccv up -d
fi

echo ""
echo "Waiting for gateway..."
END=$((SECONDS + TIMEOUT))
while [ $SECONDS -lt $END ]; do
  if curl -sf http://localhost:8000/docs > /dev/null 2>&1; then
    echo "  gateway OK  (http://localhost:8000/docs)"
    break
  fi
  sleep 2
done

if [[ "$STACK" == "qms" || "$STACK" == "all" ]]; then
  END=$((SECONDS + TIMEOUT))
  while [ $SECONDS -lt $END ]; do
    if curl -sf http://localhost:8020/docs > /dev/null 2>&1; then
      echo "  documents OK  (http://localhost:8020/docs)"
      break
    fi
    sleep 2
  done
fi

echo ""
echo "Containers are grouped in Docker Desktop as:"
echo "  rainerinfra / rainerplatform / rainerqms / rainerem / rainerccv"
