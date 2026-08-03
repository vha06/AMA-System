import asyncio
import concurrent.futures
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from src.agents.scraper.tools.search import DuckDuckGoSearchTool
from src.agents.scraper.tools.web_scraper import WebScraperTool


class SearchToolInput(BaseModel):
    """Input schema cho MarketSearchCrewTool."""
    query: str = Field(..., description="Từ khóa tìm kiếm thông tin thị trường trên DuckDuckGo.")


class MarketSearchCrewTool(BaseTool):
    name: str = "duckduckgo_market_search"
    description: str = (
        "Tìm kiếm thông tin thị trường, đối thủ, xu hướng và nhu cầu khách hàng từ DuckDuckGo. "
        "Truyền vào từ khóa tìm kiếm."
    )
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str) -> str:
        tool = DuckDuckGoSearchTool()
        results = tool.search(query, max_results=5)
        if not results:
            return f"Không tìm thấy kết quả nào cho từ khóa: '{query}'"

        output = []
        for r in results:
            output.append(f"Tiêu đề: {r.title}\nURL: {r.url}\nTóm tắt: {r.snippet}\n")
        return "\n---\n".join(output)


class ScrapeToolInput(BaseModel):
    """Input schema cho WebScraperCrewTool."""
    url: str = Field(..., description="Đường dẫn URL của trang web cần cào nội dung chi tiết.")


class WebScraperCrewTool(BaseTool):
    name: str = "web_content_scraper"
    description: str = (
        "Cào và đọc nội dung chi tiết của một trang web từ URL. "
        "Sử dụng khi cần đọc sâu bài viết, báo cáo hoặc thông tin chi tiết từ một liên kết."
    )
    args_schema: Type[BaseModel] = ScrapeToolInput

    def _run(self, url: str) -> str:
        tool = WebScraperTool()

        def _do_scrape():
            return asyncio.run(tool.scrape_url(url))

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                res = pool.submit(_do_scrape).result()
        else:
            res = _do_scrape()

        if res.error:
            return f"Lỗi khi cào trang {url}: {res.error}. Nội dung fallback: {res.clean_text}"
        return f"Trang web: {res.title} ({res.url})\n\nNội dung:\n{res.clean_text[:3000]}"
