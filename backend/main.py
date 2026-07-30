from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import router_api, scraper_api, knowledge_api, insight_api
from src.database.cache_db import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to Redis
    await cache.connect()
    yield
    # Disconnect from Redis
    await cache.disconnect()

app = FastAPI(
    title="AMA-System Backend",
    description="Automated Market Analysis System API",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(router_api, prefix="/api/v1")
app.include_router(scraper_api, prefix="/api/v1")
app.include_router(knowledge_api, prefix="/api/v1")
app.include_router(insight_api, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to AMA-System API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ama-backend"}
