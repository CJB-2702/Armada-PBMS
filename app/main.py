from fastapi import FastAPI
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.load_default_data import init_default_data

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    if settings.DEBUG:
        db = SessionLocal()
        try:
            init_default_data(db)
        finally:
            db.close()

# ... rest of your FastAPI application code ... 