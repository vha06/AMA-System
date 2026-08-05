import logging
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.config import settings, get_google_model_chain
from src.agents.router.schemas import RouterDecision, IntentType
from src.agents.router.prompts import ROUTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class RouterAgent:
    """Router Agent classification engine using Google API."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.ROUTER_LLM_MODEL
        self._client = None

        if self.api_key:
            self._client = genai.Client(api_key=self.api_key)
        else:
            logger.warning(
                "GEMINI_API_KEY is not set. RouterAgent will operate in fallback mode."
            )

    def _call_gemini_api(self, query: str) -> RouterDecision:
        """Execute call to Google API with Waterfall model chain fallback."""
        if not self._client:
            raise ValueError("GEMINI_API_KEY is required to call Google API.")

        config = types.GenerateContentConfig(
            system_instruction=ROUTER_SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=RouterDecision,
            temperature=0.1,
        )

        candidate_models = get_google_model_chain(self.model_name)

        last_exception = None

        for model in candidate_models:
            try:
                response = self._client.models.generate_content(
                    model=model,
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
            except Exception as e:
                logger.warning(f"Gemini model {model} failed in RouterAgent ({e}). Trying next in chain...")
                last_exception = e

        raise last_exception or ValueError("Empty response received from all Gemini API models.")

    def _fast_path_filter(self, query: str) -> RouterDecision | None:
        """Fast-path filter to instantly reject obvious out-of-scope queries without calling LLM."""
        q_lower = query.strip().lower()
        words = q_lower.split()

        market_keywords = [
            "thị trường", "ngách", "sản phẩm", "bán", "kinh doanh", "đối thủ",
            "giá", "tiktok", "shopee", "lazada", "amazon", "phân tích", "khách hàng",
            "chiến lược", "seo", "marketing", "doanh thu", "lợi nhuận", "chi phí",
            "f&b", "công nghệ", "mỹ phẩm", "thời trang", "đồ ăn", "xe", "bất động sản",
            "nhà đất", "đầu tư", "phần mềm", "ai", "dịch vụ", "đào tạo", "khóa học"
        ]
        has_market_keyword = any(kw in q_lower for kw in market_keywords)

        # 1. Rất ngắn (dưới 4 từ) và không có từ khóa kinh doanh/ngành nghề
        if len(words) < 4 and not has_market_keyword:
            return RouterDecision(
                intent=IntentType.OUT_OF_SCOPE,
                confidence=0.95,
                reasoning="Fast-path: Câu hỏi quá ngắn (dưới 4 từ) và không chứa thông tin kinh doanh.",
                clarification_needed="Bạn muốn phân tích ngách sản phẩm hay thị trường nào? Vui lòng mô tả chi tiết hơn.",
            )

        # 2. Danh sách các cụm từ/mẫu câu ngoài lề điển hình
        out_of_scope_patterns = [
            "xin chào", "hello", "hi", "chào bạn", "chào em", "chào anh", "chào chị",
            "thời tiết", "thứ mấy", "ngày mấy", "mấy giờ", "bạn là ai", "tên là gì",
            "chúc ngon miệng", "chúc buổi sáng", "tạm biệt", "bye", "hôm nay là thứ mấy",
            "năm nay", "hôm nay", "ngày mai", "ở đâu", "khi nào", "thế nào", "đẹp không", "tốt không"
        ]

        # Nếu phát hiện cụm từ ngoài lề VÀ không hề chứa bất kỳ từ khóa kinh doanh nào
        is_explicit_out_of_scope = any(p in q_lower for p in out_of_scope_patterns)
        if is_explicit_out_of_scope and not has_market_keyword:
            return RouterDecision(
                intent=IntentType.OUT_OF_SCOPE,
                confidence=0.95,
                reasoning="Fast-path: Phát hiện câu hỏi ngoài lề/giao tiếp thông thường.",
                clarification_needed="Hãy nhập tên sản phẩm hoặc ngách kinh doanh bạn muốn nghiên cứu.",
            )

        return None

    def analyze_query(self, query: str) -> RouterDecision:
        """Public interface to analyze and route user queries."""
        if not query or not query.strip():
            return RouterDecision(
                intent=IntentType.OUT_OF_SCOPE,
                confidence=1.0,
                reasoning="Yêu cầu rỗng hoặc không có nội dung.",
                clarification_needed="Vui lòng nhập nội dung câu hỏi hoặc yêu cầu nghiên cứu thị trường.",
            )

        # Check fast-path filter first to bypass LLM latency for non-business chats
        fast_path_decision = self._fast_path_filter(query)
        if fast_path_decision:
            logger.info(f"Fast-path filter matched for query: '{query}' -> OUT_OF_SCOPE")
            return fast_path_decision

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
