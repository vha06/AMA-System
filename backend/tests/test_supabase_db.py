import pytest
from src.database.supabase_db import SupabaseService

@pytest.mark.asyncio
async def test_supabase_service_fallback():
    # Service initialized without keys should operate in fallback/mock mode
    service = SupabaseService()
    user_id = "test-user-123"
    prompt = "Thị trường giày chạy bộ 2026"
    results = {"niche": "Giày chạy bộ êm chân nhẹ nhẹ"}
    
    saved_log = await service.save_session_log(
        user_id=user_id,
        prompt=prompt,
        results=results,
        status="success",
        source_links=[{"title": "Running Shoes", "url": "https://example.com"}]
    )

    assert saved_log["user_id"] is not None
    assert saved_log["prompt"] == prompt
    assert saved_log["status"] == "success"
    assert len(saved_log["source_links"]) == 1

    sessions = await service.get_user_sessions(user_id=user_id)
    assert isinstance(sessions, list)
