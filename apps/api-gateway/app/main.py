from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_db
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


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(reviews.router)
app.include_router(settings.router)
app.include_router(dashboard.router)
