FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libfontconfig1 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY backend/shared/rainer_common /deps/rainer_common
COPY backend/shared/rainer_auth_lib /deps/rainer_auth_lib
COPY backend/shared/rainer_tenant_lib /deps/rainer_tenant_lib
RUN pip install /deps/rainer_common /deps/rainer_auth_lib /deps/rainer_tenant_lib
COPY backend/platform/reporting-service/pyproject.toml /app/
RUN pip install -e /app
COPY backend/platform/reporting-service /app

FROM base AS production
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
EXPOSE 8010
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8010/health/live || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "2"]
