from fastapi import APIRouter

from app.api.routes.v1.underlyings import router as underlyings_router
from app.api.routes.v1.options import router as options_router
from app.api.routes.v1.signals import router as signals_router


router = APIRouter(
    prefix="/api/v1",
)


router.include_router(underlyings_router)
router.include_router(options_router)
router.include_router(signals_router)
