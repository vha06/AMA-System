import json
import logging
from typing import Optional
from redis import asyncio as aioredis
from upstash_redis.asyncio import Redis as UpstashRedis

from src.core.config import settings
from src.agents.router.schemas import RouterDecision

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.client = None
        self._connected = False
        self._is_upstash = False

    async def connect(self):
        """Connect to Redis or Upstash Redis on startup."""
        if self._connected:
            return

        # 1. Try Upstash REST API credentials first if provided
        if settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN:
            try:
                self.client = UpstashRedis(
                    url=settings.UPSTASH_REDIS_REST_URL,
                    token=settings.UPSTASH_REDIS_REST_TOKEN
                )
                self._connected = True
                self._is_upstash = True
                logger.info("Connected to Upstash Redis REST API cache successfully.")
                return
            except Exception as e:
                logger.error(f"Failed to connect to Upstash Redis REST cache: {e}")
                self._connected = False

        # 2. Fallback to standard Redis TCP URL if provided
        if settings.REDIS_URL:
            try:
                self.client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                await self.client.ping()
                self._connected = True
                self._is_upstash = False
                logger.info("Connected to standard Redis cache successfully.")
                return
            except Exception as e:
                logger.error(f"Failed to connect to standard Redis cache: {e}")
                self._connected = False

        logger.info("No valid Redis / Upstash Redis configuration provided. Operating without caching.")

    async def disconnect(self):
        """Disconnect from Redis on shutdown."""
        if self.client and self._connected:
            if not self._is_upstash and hasattr(self.client, 'aclose'):
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
                data = json.loads(cached_data) if isinstance(cached_data, str) else cached_data
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
            if self._is_upstash:
                await self.client.set(cache_key, data, ex=ttl)
            else:
                await self.client.set(cache_key, data, ex=ttl)
            logger.info(f"Cached decision for query: '{query}'")
        except Exception as e:
            logger.error(f"Redis set error: {e}")

cache = CacheService()
