from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from app.api.routes.health import router as health_router
from app.api.routes.v1.router import router as v1_router
from app.api.routes.market import router as market_router
from app.api.routes.analysis import router as analysis_router


app = FastAPI(
    title=settings.APP_NAME,
    description="Live Options Intelligence and Manual Trading System",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Routes
app.include_router(health_router)


# API V1 Routes
app.include_router(v1_router)


# Market Routes
app.include_router(
    market_router,
    prefix="/api/v1",
)


# Analysis Routes
app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "version": "0.1.0",
    }