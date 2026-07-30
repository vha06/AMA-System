import logging
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.config import settings
from src.agents.router.schemas import RouterDecision, IntentType
from src.agents.router.prompts import ROUTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class RouterAgent:
    """Router Agent classification engine using Gemini 3.1 Pro API (Free Tier)."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self._client = None

        if self.api_key:
            self._client = genai.Client(api_key=self.api_key)
        else:
            logger.warning(
                "GEMINI_API_KEY is not set. RouterAgent will operate in fallback mode."
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, Exception)),
        reraise=False,
    )
    def _call_gemini_api(self, query: str) -> RouterDecision:
        """Execute call to Gemini 3.1 Pro with rate-limit retries and structured output."""
        if not self._client:
            raise ValueError("GEMINI_API_KEY is required to call Gemini API.")

        config = types.GenerateContentConfig(
            system_instruction=ROUTER_SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=RouterDecision,
            temperature=0.1,
        )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=query,
            config=config,
        )

        if hasattr(response, "parsed") and response.parsed is not None:
            if isinstance(response.parsed, RouterDecision):
                return response.parsed
            return RouterDecision.model_validate(response.parsed)

        if response.text:
            data = json.loads(response.text)
            return RouterDecision.model_validate(data)

        raise ValueError("Empty response received from Gemini API.")

    def analyze_query(self, query: str) -> RouterDecision:
        """Public interface to analyze and route user queries."""
        if not query or not query.strip():
            return RouterDecision(
                intent=IntentType.OUT_OF_SCOPE,
                confidence=1.0,
                reasoning="Yêu cầu rỗng hoặc không có nội dung.",
                clarification_needed="Vui lòng nhập nội dung câu hỏi hoặc yêu cầu nghiên cứu thị trường.",
            )

        if not self.api_key:
            return self._heuristic_fallback(query)

        try:
            return self._call_gemini_api(query)
        except Exception as e:
            logger.error(f"Error calling Gemini API for router analysis: {e}")
            return self._heuristic_fallback(query)

    def _heuristic_fallback(self, query: str) -> RouterDecision:
        """Heuristic-based fallback classifier if API key is missing or API fails."""
        q_lower = query.lower()
        market_keywords = [
            "thị trường",
            "ngách",
            "sản phẩm",
            "bán",
            "kinh doanh",
            "đối thủ",
            "giá",
            "tiktok",
            "shopee",
            "phân tích",
            "khách hàng",
        ]
        qa_keywords = ["là gì", "khái niệm", "định nghĩa", "công thức tính", "nghĩa là gì"]

        if any(kw in q_lower for kw in market_keywords):
            return RouterDecision(
                intent=IntentType.MARKET_RESEARCH,
                confidence=0.7,
                reasoning="Fallback heuristic: Phát hiện các từ khóa nghiên cứu thị trường/kinh doanh.",
                niche_or_topic=query[:50],
            )
        elif any(kw in q_lower for kw in qa_keywords):
            return RouterDecision(
                intent=IntentType.GENERAL_QA,
                confidence=0.7,
                reasoning="Fallback heuristic: Phát hiện từ khóa hỏi đáp kiến thức tổng quan.",
            )
        else:
            return RouterDecision(
                intent=IntentType.OUT_OF_SCOPE,
                confidence=0.6,
                reasoning="Fallback heuristic: Yêu cầu không có từ khóa liên quan đến phân tích kinh doanh.",
                clarification_needed="Bạn muốn phân tích ngách sản phẩm hay thị trường nào?",
            )
