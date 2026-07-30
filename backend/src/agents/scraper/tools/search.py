import logging
from typing import List
from duckduckgo_search import DDGS
from tenacity import retry, stop_after_attempt, wait_exponential

from src.agents.scraper.schemas import SearchResultItem

logger = logging.getLogger(__name__)


class DuckDuckGoSearchTool:
    """Free Open-Source Search Tool using DuckDuckGo Search API."""

    def __init__(self, region: str = "wt-wt", max_results: int = 5):
        self.region = region
        self.max_results = max_results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=False,
    )
    def search(self, query: str, max_results: int | None = None) -> List[SearchResultItem]:
        """Execute web search query via DuckDuckGo."""
        limit = max_results or self.max_results
        results: List[SearchResultItem] = []

        if not query or not query.strip():
            return results

        try:
            logger.info(f"Searching DuckDuckGo for query: '{query}' (limit={limit})")
            with DDGS() as ddgs:
                ddg_results = ddgs.text(
                    keywords=query,
                    region=self.region,
                    safesearch="moderate",
                    max_results=limit,
                )

                if ddg_results:
                    for item in ddg_results:
                        results.append(
                            SearchResultItem(
                                title=item.get("title", ""),
                                url=item.get("href", ""),
                                snippet=item.get("body", ""),
                            )
                        )
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search for '{query}': {e}")

        return results
