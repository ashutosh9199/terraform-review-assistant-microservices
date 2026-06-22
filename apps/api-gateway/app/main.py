import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import text
from starlette.responses import Response

from app.core.config import get_settings
from app.core.database import engine, init_db
from app.core.rate_limit import InMemoryRateLimitMiddleware
from app.routers import auth, dashboard, projects, reviews, settings

app_settings = get_settings()

app = FastAPI(
    title=app_settings.app_name,
    version="0.1.0",
    description="AI-powered Azure Terraform review platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(InMemoryRateLimitMiddleware, limit=120, window_seconds=60)

# Hand-rolled metrics middleware (capstone §8 bonus: Advanced Monitoring).
# Deliberately avoids prometheus-fastapi-instrumentator: its route-name
# introspection breaks against this image's FastAPI/Starlette versions
# (AttributeError on `_IncludedRouter`). request.url.path is version-stable.
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds", ["method", "path"]
)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    path = request.url.path
    REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(duration)
    return response


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    """Liveness probe — process is up."""
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    """Readiness probe — the database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - surfaced to the probe
        raise HTTPException(status_code=503, detail=f"database not ready: {exc}") from exc
    return {"status": "ready"}


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(reviews.router)
app.include_router(settings.router)
app.include_router(dashboard.router)
