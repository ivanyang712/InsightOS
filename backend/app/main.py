from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.archetypes import router as archetypes_router
from app.api.company_research import router as company_research_router
from app.api.connectors import router as connectors_router
from app.api.demo import router as demo_router
from app.api.health import router as health_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Research infrastructure API for InsightOS.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(connectors_router)
app.include_router(archetypes_router)
app.include_router(demo_router)
app.include_router(analysis_router)
app.include_router(company_research_router)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": settings.app_name,
        "status": "running",
        "health_url": "/health",
        "docs_url": "/docs",
    }
