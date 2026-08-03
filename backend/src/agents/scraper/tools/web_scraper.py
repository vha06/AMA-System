import logging
import re
import httpx
import os
from datetime import datetime
from bs4 import BeautifulSoup
import html2text
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from src.agents.scraper.schemas import ScrapedContent, ScrapingMethod

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


class WebScraperTool:
    """Hybrid Web Scraper Tool (Static httpx + Dynamic Playwright fallback)."""

    def __init__(self, timeout_seconds: float = 15.0):
        self.timeout_seconds = timeout_seconds
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = True
        self.h2t.ignore_tables = False
        self.h2t.body_width = 0

    def _clean_html(self, html_content: str) -> tuple[str, str]:
        """Extract title and clean body text/markdown from raw HTML."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Remove useless tags
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]):
            tag.decompose()

        # Convert remaining HTML to clean text/markdown
        raw_text = self.h2t.handle(str(soup))
        # Remove multiple newlines and spaces
        clean_text = re.sub(r"\n{3,}", "\n\n", raw_text).strip()

        return title, clean_text

    async def scrape_static(self, url: str) -> tuple[str, str]:
        """Attempt fast static scraping using httpx."""
        headers = {"User-Agent": USER_AGENT}
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return self._clean_html(response.text)

    async def scrape_dynamic(self, url: str) -> tuple[str, str]:
        """Fallback dynamic scraping using Playwright headless browser with Stealth."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                ]
            )
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)
            
            try:
                await page.goto(url, timeout=int(self.timeout_seconds * 1000), wait_until="domcontentloaded")
                content = await page.content()
                title = await page.title()
                _, clean_text = self._clean_html(content)
                return title or "", clean_text
            except Exception as e:
                # Capture screenshot on failure
                screenshot_dir = os.path.join(os.path.dirname(__file__), "../../../../../logs/screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_url = re.sub(r'[^a-zA-Z0-9]', '_', url)[:50]
                screenshot_path = os.path.join(screenshot_dir, f"error_{safe_url}_{timestamp}.png")
                try:
                    await page.screenshot(path=screenshot_path)
                    logger.error(f"Dynamic scrape failed. Screenshot saved to {screenshot_path}")
                except Exception as ss_e:
                    logger.error(f"Failed to take screenshot: {ss_e}")
                raise e
            finally:
                await browser.close()

    async def scrape_url(self, url: str, title: str = "", snippet: str = "") -> ScrapedContent:
        """Scrape URL with automatic fallback from Static to Dynamic rendering."""
        logger.info(f"Scraping URL: {url}")
        
        # 1. Try static scraping first
        try:
            extracted_title, clean_text = await self.scrape_static(url)
            if len(clean_text) >= 150:
                return ScrapedContent(
                    url=url,
                    title=extracted_title or title,
                    snippet=snippet,
                    clean_text=clean_text,
                    scraped_via=ScrapingMethod.STATIC,
                )
            logger.info(f"Static scrape for {url} returned minimal content ({len(clean_text)} chars). Trying Playwright fallback...")
        except Exception as e:
            logger.warning(f"Static scrape failed for {url}: {e}. Trying Playwright fallback...")

        # 2. Try dynamic scraping (Playwright) if static failed or returned short content
        try:
            extracted_title, clean_text = await self.scrape_dynamic(url)
            if clean_text:
                return ScrapedContent(
                    url=url,
                    title=extracted_title or title,
                    snippet=snippet,
                    clean_text=clean_text,
                    scraped_via=ScrapingMethod.DYNAMIC,
                )
            else:
                return ScrapedContent(
                    url=url,
                    title=title,
                    snippet=snippet,
                    clean_text=snippet,  # Fallback to search snippet if page empty
                    scraped_via=ScrapingMethod.FAILED,
                    error="Scraped content was empty.",
                )
        except Exception as e:
            logger.error(f"Dynamic scrape also failed for {url}: {e}")
            return ScrapedContent(
                url=url,
                title=title,
                snippet=snippet,
                clean_text=snippet,  # Fallback to search snippet on failure
                scraped_via=ScrapingMethod.FAILED,
                error=str(e),
            )
