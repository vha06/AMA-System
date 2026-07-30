import json
import logging
from typing import Optional
from redis import asyncio as aioredis

from src.core.config import settings
from src.agents.router.schemas import RouterDecision

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.client: aioredis.Redis | None = None
        self._connected = False

    async def connect(self):
        """Connect to Redis on startup."""
        if not self._connected and self.redis_url:
            try:
                self.client = aioredis.from_url(self.redis_url, decode_responses=True)
                await self.client.ping()
                self._connected = True
                logger.info("Connected to Redis cache successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to Redis cache: {e}")
                self._connected = False

    async def disconnect(self):
        """Disconnect from Redis on shutdown."""
        if self.client and self._connected:
            await self.client.aclose()
            self._connected = False
            logger.info("Disconnected from Redis cache.")

    async def get_router_decision(self, query: str) -> Optional[RouterDecision]:
        """Get cached router decision for a query."""
        if not self._connected or not self.client:
            return None
            
        try:
            cache_key = f"router:decision:{query.strip().lower()}"
            cached_data = await self.client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                logger.info(f"Cache hit for query: '{query}'")
                return RouterDecision.model_validate(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None

    async def set_router_decision(self, query: str, decision: RouterDecision, ttl: int = 3600):
        """Cache router decision for a query. Default TTL is 1 hour."""
        if not self._connected or not self.client:
            return
            
        try:
            cache_key = f"router:decision:{query.strip().lower()}"
            data = decision.model_dump_json()
            await self.client.set(cache_key, data, ex=ttl)
            logger.info(f"Cached decision for query: '{query}'")
        except Exception as e:
            logger.error(f"Redis set error: {e}")

cache = CacheService()
