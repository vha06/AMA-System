import datetime
import logging
from typing import Any, Dict, List, Optional
import uuid

from src.core.config import settings

logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    Client = Any
    SUPABASE_AVAILABLE = False
    logger.warning("supabase-py library is not installed.")

class SupabaseService:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        # Use service role key if available for backend administrative writes, fallback to anon key
        self.key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
        self.client: Optional[Client] = None
        self._connected = False
        self._mock_logs: List[Dict[str, Any]] = []

        if SUPABASE_AVAILABLE and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                self._connected = True
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self._connected = False
        else:
            logger.info("Supabase is unconfigured or unavailable. Running in Mock/Fallback mode.")

    def is_connected(self) -> bool:
        return self._connected and self.client is not None

    async def save_session_log(
        self,
        user_id: str,
        prompt: str,
        results: Dict[str, Any],
        status: str = "success",
        source_links: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Save a search/analysis session log to Supabase or in-memory fallback."""
        if source_links is None:
            source_links = []

        log_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "prompt": prompt,
            "results": results,
            "status": status,
            "source_links": source_links,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        if not self.is_connected():
            logger.info(f"[Mock Mode] Session log saved in-memory: {log_data['id']} for user {user_id}")
            self._mock_logs.insert(0, log_data)
            return log_data

        try:
            response = self.client.table("session_logs").insert(log_data).execute()
            if response.data and len(response.data) > 0:
                logger.info(f"Successfully saved session log {response.data[0]['id']} for user {user_id}")
                return response.data[0]
            self._mock_logs.insert(0, log_data)
            return log_data
        except Exception as e:
            logger.error(f"Error saving session log to Supabase: {e}. Storing in mock memory.")
            self._mock_logs.insert(0, log_data)
            return log_data

    async def get_user_sessions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch all session logs for a given user ordered by created_at DESC."""
        if not self.is_connected():
            user_logs = [log for log in self._mock_logs if log.get("user_id") == user_id or user_id == "anonymous" or log.get("user_id") == "anonymous"]
            return user_logs[:limit]

        try:
            response = (
                self.client.table("session_logs")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching session logs for user {user_id}: {e}")
            user_logs = [log for log in self._mock_logs if log.get("user_id") == user_id or user_id == "anonymous" or log.get("user_id") == "anonymous"]
            return user_logs[:limit]

    async def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific session log by its ID."""
        for log in self._mock_logs:
            if log.get("id") == session_id:
                return log

        if not self.is_connected():
            return None

        try:
            response = (
                self.client.table("session_logs")
                .select("*")
                .eq("id", session_id)
                .single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error fetching session log {session_id}: {e}")
            return None

supabase_db = SupabaseService()
