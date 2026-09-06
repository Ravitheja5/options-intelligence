from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import engine


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check():
    return {
        "status": "ok",
        "service": "options-intelligence",
    }


@router.get("/db")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        ).fetchone()

    return {
        "status": "ok",
        "database": result[0],
        "user": result[1],
    }
