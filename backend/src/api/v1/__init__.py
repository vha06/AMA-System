"""API v1 package."""
from src.api.v1.router import router as router_api
from src.api.v1.scraper import router as scraper_api
from src.api.v1.knowledge import router as knowledge_api
from src.api.v1.insight import router as insight_api

__all__ = ["router_api", "scraper_api", "knowledge_api", "insight_api"]


