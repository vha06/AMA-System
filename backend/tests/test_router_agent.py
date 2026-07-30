import pytest
from fastapi.testclient import TestClient
from main import app
from src.agents.router.schemas import IntentType, RouterDecision, AnalysisRequest
from src.agents.router.agent import RouterAgent

client = TestClient(app)


def test_router_decision_schema():
    decision = RouterDecision(
        intent=IntentType.MARKET_RESEARCH,
        confidence=0.95,
        niche_or_topic="Mỹ phẩm organic",
        target_audience="Phụ nữ 20-35 tuổi",
        target_platforms=["TikTok", "Shopee"],
        reasoning="Người dùng yêu cầu phân tích ngách mỹ phẩm organic trên TikTok và Shopee.",
    )
    assert decision.intent == IntentType.MARKET_RESEARCH
    assert decision.confidence == 0.95
    assert decision.niche_or_topic == "Mỹ phẩm organic"
    assert "TikTok" in decision.target_platforms


def test_router_agent_heuristic_fallback_market():
    agent = RouterAgent(api_key="")
    query = "Phân tích ngách mỹ phẩm organic trên TikTok"
    result = agent.analyze_query(query)
    assert result.intent == IntentType.MARKET_RESEARCH
    assert result.confidence > 0.5


def test_router_agent_heuristic_fallback_qa():
    agent = RouterAgent(api_key="")
    query = "Kế toán quản trị là gì?"
    result = agent.analyze_query(query)
    assert result.intent == IntentType.GENERAL_QA


def test_router_agent_heuristic_fallback_out_of_scope():
    agent = RouterAgent(api_key="")
    query = "Thời tiết hôm nay thế nào?"
    result = agent.analyze_query(query)
    assert result.intent == IntentType.OUT_OF_SCOPE


def test_fastapi_router_endpoint():
    response = client.post(
        "/api/v1/router/analyze",
        json={"query": "Nghiên cứu thị trường quần áo thể thao nam"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "confidence" in data
    assert "reasoning" in data
    assert data["intent"] in ["MARKET_RESEARCH", "GENERAL_QA", "OUT_OF_SCOPE"]
