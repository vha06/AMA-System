from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ScrapingMethod(str, Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    FAILED = "failed"


class ScraperInput(BaseModel):
    """Input payload for Scraper Agent."""
    niche_or_topic: str = Field(..., description="Topic or niche to research and scrape")
    search_queries: Optional[List[str]] = Field(
        default=None,
        description="Optional pre-generated search queries. If None, queries will be generated."
    )
    max_results_per_query: int = Field(default=3, ge=1, le=10, description="Max search results per query")


class SearchResultItem(BaseModel):
    """Single item from DuckDuckGo search."""
    title: str = Field(..., description="Title of the search result page")
    url: str = Field(..., description="URL link")
    snippet: str = Field("", description="Short snippet/summary from search engine")


class ScrapedContent(BaseModel):
    """Content extracted from a scraped URL."""
    url: str = Field(..., description="Target URL")
    title: str = Field("", description="Page title")
    snippet: str = Field("", description="Search snippet")
    clean_text: str = Field("", description="Extracted clean body text / markdown")
    scraped_via: ScrapingMethod = Field(ScrapingMethod.STATIC, description="Scraping method used")
    error: Optional[str] = Field(None, description="Error message if scraping failed")


class ScraperOutput(BaseModel):
    """Output payload from Scraper Agent."""
    niche_or_topic: str = Field(..., description="Target niche/topic researched")
    queries_used: List[str] = Field(default_factory=list, description="Search queries executed")
    total_scraped: int = Field(0, description="Total successfully scraped web pages")
    results: List[ScrapedContent] = Field(default_factory=list, description="Scraped articles/content list")
    summary: str = Field("", description="Optional summary of overall scraped market insights")
