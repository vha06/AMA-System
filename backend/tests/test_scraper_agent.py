import pytest
from src.agents.scraper.schemas import (
    ScraperInput,
    ScraperOutput,
    ScrapedContent,
    ScrapingMethod,
    SearchResultItem,
)
from src.agents.scraper.tools.search import DuckDuckGoSearchTool
from src.agents.scraper.tools.web_scraper import WebScraperTool
from src.agents.scraper.agent import ScraperAgent


def test_scraper_schemas():
    inp = ScraperInput(niche_or_topic="Thời trang gia đình")
    assert inp.niche_or_topic == "Thời trang gia đình"
    assert inp.max_results_per_query == 3

    content = ScrapedContent(
        url="https://example.com",
        title="Example Title",
        clean_text="Example clean text content",
        scraped_via=ScrapingMethod.STATIC,
    )
    assert content.url == "https://example.com"
    assert content.scraped_via == ScrapingMethod.STATIC

    output = ScraperOutput(
        niche_or_topic="Thời trang gia đình",
        total_scraped=1,
        results=[content],
    )
    assert output.total_scraped == 1
    assert len(output.results) == 1


def test_duckduckgo_search_tool():
    tool = DuckDuckGoSearchTool(max_results=2)
    results = tool.search("thời trang gia đình")
    assert isinstance(results, list)
    # Even if network fluctuates, results should be a list of SearchResultItem
    for r in results:
        assert isinstance(r, SearchResultItem)
        assert r.url.startswith("http")


@pytest.mark.asyncio
async def test_web_scraper_html_clean():
    tool = WebScraperTool()
    sample_html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <nav>Navigation Bar</nav>
            <script>console.log('test');</script>
            <h1>Main Title</h1>
            <p>This is a test paragraph for scraping.</p>
            <footer>Footer content</footer>
        </body>
    </html>
    """
    title, clean_text = tool._clean_html(sample_html)
    assert title == "Test Page"
    assert "Main Title" in clean_text
    assert "test paragraph" in clean_text
    assert "Navigation Bar" not in clean_text
    assert "console.log" not in clean_text


@pytest.mark.asyncio
async def test_scraper_agent_heuristic_run():
    agent = ScraperAgent(api_key="", max_urls_to_scrape=2)
    payload = ScraperInput(
        niche_or_topic="Đồ chơi giáo dục trẻ em",
        max_results_per_query=1,
    )
    output = await agent.run(payload)

    assert isinstance(output, ScraperOutput)
    assert output.niche_or_topic == "Đồ chơi giáo dục trẻ em"
    assert len(output.queries_used) > 0
    assert output.total_scraped >= 0


def test_fastapi_scraper_endpoint():
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/scraper/scrape",
        json={"niche_or_topic": "Nước hoa chiết", "max_results_per_query": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["niche_or_topic"] == "Nước hoa chiết"
    assert "queries_used" in data
    assert "total_scraped" in data
    assert "results" in data

