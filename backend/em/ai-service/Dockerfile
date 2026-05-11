FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

FROM base AS builder
RUN pip install hatchling
COPY backend/shared/rainer_common /deps/rainer_common
COPY backend/shared/rainer_auth_lib /deps/rainer_auth_lib
COPY backend/shared/rainer_tenant_lib /deps/rainer_tenant_lib
RUN pip install /deps/rainer_common /deps/rainer_auth_lib /deps/rainer_tenant_lib
COPY backend/em/ai-service/pyproject.toml /app/
RUN pip install -e /app
COPY backend/em/ai-service /app

FROM base AS production
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
USER appuser
EXPOSE 8032
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8032/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8032"]
