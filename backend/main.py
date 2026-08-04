import os
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import router_api, scraper_api, knowledge_api, insight_api, crew_api
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
origins_env = os.getenv("CORS_ORIGINS", "*")
if origins_env == "*":
    cors_origins = ["*"]
    cors_regex = ".*"
else:
    raw_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    cors_origins = [o for o in raw_origins if "*" not in o]
    # Convert wildcard patterns like https://*.vercel.app into regex
    regex_parts = []
    for o in raw_origins:
        if "*" in o:
            pattern = re.escape(o).replace(r"\*", r".*")
            regex_parts.append(f"^{pattern}$")
    cors_regex = "|".join(regex_parts) if regex_parts else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_origin_regex=cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(router_api, prefix="/api/v1")
app.include_router(scraper_api, prefix="/api/v1")
app.include_router(knowledge_api, prefix="/api/v1")
app.include_router(insight_api, prefix="/api/v1")
app.include_router(crew_api, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to AMA-System API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ama-backend"}
