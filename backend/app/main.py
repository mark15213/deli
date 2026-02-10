# FastAPI application entry point
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.core.config import get_settings
from app.api import api_router
from app.core.database import async_session_maker
from app.core.debug_data import reseed_debug_sources
from app.core.seed_data import reset_seed_data

from app.core.logging_config import setup_logging

settings = get_settings()

# Initialize logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Dev mode: seed test data
    if settings.dev_mode:
        print("Dev mode enabled - seeding test data...")
        try:
            async with async_session_maker() as db:
                await reseed_debug_sources(db)
                await reset_seed_data(db)
            print("Test data seeded successfully.")
        except Exception as e:
            print(f"Startup warning: Failed to seed data: {e}")
    
    # Start background sync scheduler
    from app.background.sync_scheduler import start_scheduler_task, stop_scheduler
    await start_scheduler_task()
    print("Background sync scheduler started.")
    
    yield
    # Shutdown
    stop_scheduler()
    print("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Deli API - Transform Notion notes into spaced repetition quizzes",
    lifespan=lifespan,
    redirect_slashes=False,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for extracted PDF figures
from fastapi.staticfiles import StaticFiles
from pathlib import Path

static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)
(static_dir / "images").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include API routes
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


# Dev mode: manual reseed endpoint
if settings.dev_mode:
    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import get_db
    
    @app.post("/dev/reseed")
    async def manual_reseed(db: AsyncSession = Depends(get_db)):
        """Manually reset seed data (dev only)."""
        await reset_seed_data(db)
        return {"status": "reseeded"}

