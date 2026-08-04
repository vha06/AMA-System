import logging
import json
from typing import Generator
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.config import settings, get_gemini_model_chain
from src.agents.insight.schemas import InsightReport, PricingStrategy
from src.agents.insight.prompts import INSIGHT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class InsightAgent:
    """Strategic Insight Agent utilizing Gemini API to produce business insight reports."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self._client = None

        if self.api_key:
            self._client = genai.Client(api_key=self.api_key)
        else:
            logger.warning(
                "GEMINI_API_KEY is not set. InsightAgent will operate in fallback mode."
            )

    def _call_gemini_api(self, topic: str, context_data: str) -> InsightReport:
        """Execute call to Gemini API with Waterfall model chain fallback."""
        if not self._client:
            raise ValueError("GEMINI_API_KEY is required to call Gemini API.")

        prompt = f"Chủ đề phân tích: {topic}\n\nDữ liệu bối cảnh (Context Data):\n{context_data}"
        config = types.GenerateContentConfig(
            system_instruction=INSIGHT_SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=InsightReport,
            temperature=0.2,
        )

        candidate_models = get_gemini_model_chain(self.model_name)
        last_exception = None

        for model in candidate_models:
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )

                if hasattr(response, "parsed") and response.parsed is not None:
                    if isinstance(response.parsed, InsightReport):
                        return response.parsed
                    return InsightReport.model_validate(response.parsed)

                if response.text:
                    data = json.loads(response.text)
                    return InsightReport.model_validate(data)
            except Exception as e:
                logger.warning(f"Gemini model {model} failed in _call_gemini_api ({e}). Trying next in chain...")
                last_exception = e

        raise last_exception or ValueError("Empty response received from all Gemini API models.")

    def analyze_insight(self, topic: str, context_data: str = "") -> InsightReport:
        """Public interface to generate strategic insights from topic and context."""
        if not topic or not topic.strip():
            return self._heuristic_fallback("Chủ đề rỗng", context_data)

        if not self.api_key:
            return self._heuristic_fallback(topic, context_data)

        try:
            return self._call_gemini_api(topic, context_data)
        except Exception as e:
            logger.error(f"Error calling Gemini API for insight generation: {e}")
            return self._heuristic_fallback(topic, context_data)

    def stream_insight(self, topic: str, context_data: str = "") -> Generator[str, None, None]:
        """Stream raw JSON chunks of strategic insights for Vercel AI SDK streamObject."""
        if not topic or not topic.strip():
            yield from self._stream_heuristic_fallback("Chủ đề rỗng", context_data)
            return

        if not self.api_key or not self._client:
            yield from self._stream_heuristic_fallback(topic, context_data)
            return

        prompt = f"Chủ đề phân tích: {topic}\n\nDữ liệu bối cảnh (Context Data):\n{context_data}"
        config = types.GenerateContentConfig(
            system_instruction=INSIGHT_SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=InsightReport,
            temperature=0.2,
        )

        candidate_models = get_gemini_model_chain(self.model_name)

        for model in candidate_models:
            try:
                response_stream = self._client.models.generate_content_stream(
                    model=model,
                    contents=prompt,
                    config=config,
                )

                has_yielded = False
                for chunk in response_stream:
                    if chunk.text:
                        has_yielded = True
                        yield chunk.text

                if has_yielded:
                    return
            except Exception as e:
                logger.warning(f"Gemini model {model} failed ({e}). Trying next model if available...")

        logger.error("All Gemini API models failed. Falling back to heuristic mock response.")
        yield from self._stream_heuristic_fallback(topic, context_data)

    def _stream_heuristic_fallback(
        self, topic: str, context_data: str
    ) -> Generator[str, None, None]:
        """Fallback generator that yields heuristic response as raw JSON chunks."""
        logger.info("Using streaming heuristic fallback for InsightAgent.")
        fallback_report = self._heuristic_fallback(topic, context_data)
        json_str = fallback_report.model_dump_json()

        # Stream in chunk sizes (e.g. 50 chars) to simulate streaming
        chunk_size = 50
        for i in range(0, len(json_str), chunk_size):
            yield json_str[i : i + chunk_size]

    def _heuristic_fallback(self, topic: str, context_data: str) -> InsightReport:
        """Fallback generator when API key is missing or API call fails."""
        logger.info("Using heuristic fallback for InsightAgent.")
        return InsightReport(
            niche_analysis=f"Thị trường '{topic}' có tiềm năng phát triển tốt. Cần tập trung vào trải nghiệm khách hàng và các góc tiếp cận ngách ít đối thủ cạnh tranh.",
            pricing=PricingStrategy(
                suggested_price="200,000 - 500,000 VNĐ",
                rationale="Mức giá phù hợp cho thị trường phổ thông tại Việt Nam, dễ thu hút người dùng trải nghiệm lần đầu.",
            ),
            risks=[
                "Cạnh tranh gay gắt về giá từ các thương hiệu lớn.",
                "Biến động chi phí quảng cáo và thu hút khách hàng (CAC).",
                "Phụ thuộc vào chính sách của các nền tảng mạng xã hội/sàn e-commerce.",
            ],
            seo_keywords=[
                topic.lower(),
                f"kinh doanh {topic.lower()}",
                f"ngách {topic.lower()}",
                "xu hướng thị trường",
                "chiến lược giá tốt nhất",
            ],
            ai_prompts=[
                f"Hãy viết 5 tiêu đề bài viết viral về chủ đề {topic}.",
                f"Tạo kịch bản video TikTok 30 giây giới thiệu giải pháp cho ngách {topic}.",
                f"Lập danh sách 10 câu hỏi thường gặp của khách hàng trong ngành {topic}.",
            ],
        )

