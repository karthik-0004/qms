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
COPY backend/ccv/technician-service/pyproject.toml /app/
RUN pip install -e /app
COPY backend/ccv/technician-service /app

FROM base AS production
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8043
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8043/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8043", "--workers", "1"]
