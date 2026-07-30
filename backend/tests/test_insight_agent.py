import pytest
from unittest.mock import MagicMock, patch
from src.agents.insight.schemas import InsightReport, PricingStrategy
from src.agents.insight.agent import InsightAgent


def test_insight_report_schema():
    report = InsightReport(
        niche_analysis="Ngách mỹ phẩm thiên nhiên có dung lượng thị trường lớn.",
        pricing=PricingStrategy(
            suggested_price="300,000 - 450,000 VNĐ",
            rationale="Độ phân khúc trung bình phù hợp với học sinh sinh viên và người đi làm.",
        ),
        risks=["Hàng giả hàng nhái nhiều", "Chi phí Marketing cao"],
        seo_keywords=["mỹ phẩm thiên nhiên", "skincare hữu cơ"],
        ai_prompts=["Viết bài content về skincare"],
    )
    assert report.niche_analysis.startswith("Ngách mỹ phẩm")
    assert report.pricing.suggested_price == "300,000 - 450,000 VNĐ"
    assert len(report.risks) == 2
    assert len(report.seo_keywords) == 2
    assert len(report.ai_prompts) == 1


def test_insight_agent_heuristic_fallback():
    agent = InsightAgent(api_key="")
    report = agent.analyze_insight("Thời trang nam", context_data="Dữ liệu mẫu từ TikTok")
    assert isinstance(report, InsightReport)
    assert "Thời trang nam" in report.niche_analysis
    assert report.pricing.suggested_price != ""
    assert len(report.risks) > 0
    assert len(report.seo_keywords) > 0
    assert len(report.ai_prompts) > 0


def test_insight_agent_empty_topic_fallback():
    agent = InsightAgent(api_key="fake_key")
    report = agent.analyze_insight("", context_data="")
    assert isinstance(report, InsightReport)
    assert report.niche_analysis != ""


@patch("src.agents.insight.agent.genai.Client")
def test_insight_agent_mock_gemini_api(mock_genai_client):
    mock_instance = MagicMock()
    mock_genai_client.return_value = mock_instance

    mock_parsed_report = InsightReport(
        niche_analysis="Phân tích ngách thành công từ Gemini",
        pricing=PricingStrategy(
            suggested_price="150,000 VNĐ",
            rationale="Giá cạnh tranh",
        ),
        risks=["Rủi ro A"],
        seo_keywords=["từ khóa A"],
        ai_prompts=["Prompt A"],
    )

    mock_response = MagicMock()
    mock_response.parsed = mock_parsed_report
    mock_instance.models.generate_content.return_value = mock_response

    agent = InsightAgent(api_key="test_key")
    result = agent.analyze_insight("Tai nghe Bluetooth", context_data="Context test")

    assert result.niche_analysis == "Phân tích ngách thành công từ Gemini"
    assert result.pricing.suggested_price == "150,000 VNĐ"
    assert result.risks == ["Rủi ro A"]


def test_insight_agent_stream_fallback():
    agent = InsightAgent(api_key="")
    chunks = list(agent.stream_insight("Thời trang nam", context_data="Dữ liệu mẫu từ TikTok"))
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert "niche_analysis" in full_text
    assert "Thời trang nam" in full_text


@patch("src.agents.insight.agent.genai.Client")
def test_insight_agent_stream_mock(mock_genai_client):
    mock_instance = MagicMock()
    mock_genai_client.return_value = mock_instance

    mock_chunk1 = MagicMock()
    mock_chunk1.text = '{"niche_analysis": "Phân tích'
    mock_chunk2 = MagicMock()
    mock_chunk2.text = ' ngách thành công"}'

    mock_instance.models.generate_content_stream.return_value = [mock_chunk1, mock_chunk2]

    agent = InsightAgent(api_key="test_key")
    chunks = list(agent.stream_insight("Tai nghe Bluetooth", context_data="Context test"))

    assert chunks == ['{"niche_analysis": "Phân tích', ' ngách thành công"}']

