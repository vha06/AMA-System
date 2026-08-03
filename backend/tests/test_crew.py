import pytest
from fastapi.testclient import TestClient
from main import app
from src.agents.crew.tools.crew_tools import MarketSearchCrewTool, WebScraperCrewTool
from src.agents.crew.agents import create_router_agent, create_scraper_agent, create_insight_agent

client = TestClient(app)


def test_crew_tools_initialization():
    search_tool = MarketSearchCrewTool()
    scraper_tool = WebScraperCrewTool()
    
    assert search_tool.name == "duckduckgo_market_search"
    assert scraper_tool.name == "web_content_scraper"


def test_crew_agents_creation():
    router = create_router_agent()
    scraper = create_scraper_agent()
    insight = create_insight_agent()
    
    assert "Router Agent" in router.role
    assert "Scraper Agent" in scraper.role
    assert "Insight Agent" in insight.role


def test_crew_stream_endpoint_validation():
    # Test empty query validation
    response = client.post("/api/v1/crew/stream", json={"query": ""})
    assert response.status_code == 400
    assert "Truy vấn không được để rỗng" in response.json()["detail"]
