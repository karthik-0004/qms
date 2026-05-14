docker compose -f docker-compose.platform.yml up -d                 # Start platform stack in background
docker compose -f docker-compose.platform.yml up -d gateway-service # Start only gateway-service (and required dependencies)
docker compose -f docker-compose.platform.yml logs -f gateway-service # Follow gateway-service logs (live)
docker compose -f docker-compose.platform.yml restart gateway-service # Restart gateway-service container
docker compose -f docker-compose.platform.yml ps                    # Show status of platform containers
docker compose -f docker-compose.platform.yml down                  # Stop and remove platform containers + network
docker compose -f docker-compose.platform.yml down -v               # Stop and remove containers + DELETE named volumes (data reset)