import asyncio
import json
import logging
from typing import List
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.config import settings, get_gemini_model_chain
from src.agents.scraper.schemas import (
    ScraperInput,
    ScraperOutput,
    ScrapedContent,
    SearchResultItem,
)
from src.agents.scraper.prompts import (
    SCRAPER_QUERY_GEN_PROMPT,
    SCRAPER_SUMMARY_PROMPT,
)
from src.agents.scraper.tools.search import DuckDuckGoSearchTool
from src.agents.scraper.tools.web_scraper import WebScraperTool

logger = logging.getLogger(__name__)


class ScraperAgent:
    """Open-Source Zero-Cost Market Research Scraper Agent."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        max_urls_to_scrape: int = 5,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.max_urls_to_scrape = max_urls_to_scrape
        self.search_tool = DuckDuckGoSearchTool()
        self.scraper_tool = WebScraperTool()
        self._client = None

        if self.api_key:
            self._client = genai.Client(api_key=self.api_key)
        else:
            logger.warning(
                "GEMINI_API_KEY is not set. ScraperAgent will use fallback query generation."
            )

    def _generate_queries(self, niche_or_topic: str) -> List[str]:
        """Generate search queries for the niche using Gemini 3.1 Pro or fallback."""
        if not self._client:
            return self._heuristic_query_expansion(niche_or_topic)

        prompt = f"{SCRAPER_QUERY_GEN_PROMPT}\n\nNiche/Topic: {niche_or_topic}"
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        )

        candidate_models = get_gemini_model_chain(self.model_name)

        for model in candidate_models:
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )

                if response.text:
                    data = json.loads(response.text)
                    if isinstance(data, list):
                        return [str(q) for q in data[:3]]
                    elif isinstance(data, dict) and "queries" in data:
                        return [str(q) for q in data["queries"][:3]]
            except Exception as e:
                logger.warning(f"Gemini model {model} failed in _generate_queries ({e}). Trying next in chain...")

        return self._heuristic_fallback_queries(niche_or_topic)

    def _heuristic_query_expansion(self, niche_or_topic: str) -> List[str]:
        """Generate static heuristic queries if LLM is unavailable."""
        return [
            f"thị trường {niche_or_topic} xu hướng 2026",
            f"báo cáo phân tích đối thủ sản phẩm {niche_or_topic}",
            f"nhu cầu giá cả khách hàng {niche_or_topic}",
        ]

    def _heuristic_fallback_queries(self, niche_or_topic: str) -> List[str]:
        return [
            f"phân tích thị trường {niche_or_topic}",
            f"xu hướng kinh doanh {niche_or_topic}",
        ]

    async def run(self, payload: ScraperInput) -> ScraperOutput:
        """Run full scraping workflow asynchronously."""
        niche = payload.niche_or_topic.strip()
        logger.info(f"Starting ScraperAgent for topic: '{niche}'")

        # 1. Determine search queries
        queries = payload.search_queries
        if not queries:
            queries = self._generate_queries(niche)
        logger.info(f"Using search queries: {queries}")

        # 2. Search DuckDuckGo for all queries
        all_search_items: List[SearchResultItem] = []
        for q in queries:
            items = self.search_tool.search(q, max_results=payload.max_results_per_query)
            all_search_items.extend(items)

        # Deduplicate search results by URL
        unique_items_dict = {}
        for item in all_search_items:
            if item.url and item.url not in unique_items_dict:
                unique_items_dict[item.url] = item

        items_to_scrape = list(unique_items_dict.values())[: self.max_urls_to_scrape]
        logger.info(f"Found {len(unique_items_dict)} unique URLs, scraping top {len(items_to_scrape)}")

        # 3. Concurrently scrape content from URLs
        scrape_tasks = [
            self.scraper_tool.scrape_url(url=item.url, title=item.title, snippet=item.snippet)
            for item in items_to_scrape
        ]
        scraped_results: List[ScrapedContent] = await asyncio.gather(*scrape_tasks)

        successful_count = sum(1 for r in scraped_results if r.clean_text and r.scraped_via != "failed")

        # 4. Generate optional summary if LLM client available
        summary_text = ""
        if self._client and scraped_results:
            summary_text = self._summarize_findings(niche, scraped_results)

        return ScraperOutput(
            niche_or_topic=niche,
            queries_used=queries,
            total_scraped=successful_count,
            results=scraped_results,
            summary=summary_text,
        )

    def _summarize_findings(self, niche: str, results: List[ScrapedContent]) -> str:
        """Summarize scraped text content using Gemini API with model fallback."""
        try:
            combined_texts = []
            for r in results[:3]:
                if r.clean_text:
                    combined_texts.append(f"Source: {r.title} ({r.url})\n{r.clean_text[:1000]}")
            
            context = "\n\n---\n\n".join(combined_texts)
            prompt = SCRAPER_SUMMARY_PROMPT.format(niche_or_topic=niche) + f"\n\nData:\n{context}"

            candidate_models = get_gemini_model_chain(self.model_name)

            for model in candidate_models:
                try:
                    response = self._client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )
                    if response.text:
                        return response.text.strip()
                except Exception as e:
                    logger.warning(f"Gemini model {model} failed in _summarize_findings ({e}). Trying next in chain...")

            return ""
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return ""
