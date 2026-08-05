from crewai import Agent, LLM
from src.core.config import settings
from src.agents.crew.tools.crew_tools import MarketSearchCrewTool, WebScraperCrewTool


def get_llm(model_name: str | None = None) -> LLM:
    """Khởi tạo cấu hình LLM cho CrewAI."""
    target_model = model_name or settings.LLM_MODEL
    return LLM(
        model=f"gemini/{target_model}",
        api_key=settings.GEMINI_API_KEY or "dummy_key",
        temperature=0.2,
    )


def create_router_agent() -> Agent:
    """Agent chịu trách nhiệm phân tích ý định và trích xuất ngách thị trường."""
    return Agent(
        role="Chuyên viên Phân luồng & Ý định Thị trường (Router Agent)",
        goal="Phân tích yêu cầu của người dùng, xác định xem yêu cầu đó có thuộc phạm vi nghiên cứu thị trường hay không, và trích xuất từ khóa/ngách chính xác.",
        backstory=(
            "Bạn là một chuyên gia phân tích dữ liệu đầu vào. Bạn có khả năng lắng nghe yêu cầu kinh doanh của người dùng "
            "và phân loại chính xác xem họ muốn tìm hiểu về thị trường/sản phẩm gì để định hướng cho đội ngũ nghiên cứu."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm(settings.ROUTER_LLM_MODEL),
    )


def create_scraper_agent() -> Agent:
    """Agent chịu trách nhiệm tìm kiếm và cào dữ liệu thị trường thực tế."""
    return Agent(
        role="Chuyên viên Thu thập & Dữ liệu Thị trường (Scraper Agent)",
        goal="Sử dụng công cụ tìm kiếm DuckDuckGo và cào dữ liệu trang web để thu thập thông tin về đối thủ, giá cả, và xu hướng thực tế.",
        backstory=(
            "Bạn là một nhà điều tra thị trường số tinh nhuệ. Bạn biết cách chọn lọc từ khóa tìm kiếm thông minh, "
            "truy cập các bài viết phân tích, báo cáo ngành và cào dữ liệu chất lượng cao phục vụ cho phân tích chiến lược."
        ),
        tools=[MarketSearchCrewTool(), WebScraperCrewTool()],
        verbose=True,
        allow_delegation=False,
        llm=get_llm(settings.SCRAPER_LLM_MODEL),
    )


def create_insight_agent() -> Agent:
    """Agent chịu trách nhiệm phân tích chiến lược và tổng hợp báo cáo."""
    return Agent(
        role="Chuyên gia Phân tích Chiến lược & Insight (Insight Agent)",
        goal="Tổng hợp tất cả dữ liệu đã thu thập được để xây dựng báo cáo phân tích thị trường toàn diện bao gồm: Phân tích ngách, Chiến lược giá, Từ khóa SEO và Đánh giá Rủi ro.",
        backstory=(
            "Bạn là Giám đốc Chiến lược Kinh doanh (Chief Strategy Officer) giàu kinh nghiệm. Bạn có tư duy phản biện sắc bén, "
            "khả năng biến các dữ liệu thô thành các góc nhìn kinh doanh thực chiến và đề xuất chiến lược tối ưu cho người dùng."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm(settings.INSIGHT_LLM_MODEL),
    )
