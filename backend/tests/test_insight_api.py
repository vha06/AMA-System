import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_stream_insight_endpoint():
    response = client.post(
        "/api/v1/insight/stream",
        json={"topic": "Cafe Mèo", "context_data": "Thị trường ngách thành phố lớn"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    content = response.text
    assert len(content) > 0
    assert "niche_analysis" in content
    assert "Cafe Mèo" in content
