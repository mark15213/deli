from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import api_router

app = FastAPI(title="Gulp API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to Gulp API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
