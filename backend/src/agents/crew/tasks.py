from crewai import Task, Agent
from src.agents.insight.schemas import InsightReport


def create_intent_task(agent: Agent, user_query: str) -> Task:
    """Tạo Task phân tích ý định cho Router Agent."""
    return Task(
        description=(
            f"Phân tích truy vấn của người dùng: '{user_query}'. "
            "Xác định ngách thị trường/sản phẩm chính mà người dùng muốn phân tích. "
            "Rút ra danh sách 2-3 từ khóa tìm kiếm chất lượng cao về thị trường này."
        ),
        expected_output="Thông tin ngách thị trường chính và danh sách các từ khóa tìm kiếm đề xuất.",
        agent=agent,
    )


def create_scrape_task(agent: Agent) -> Task:
    """Tạo Task thu thập dữ liệu thị trường cho Scraper Agent."""
    return Task(
        description=(
            "Dựa trên ngách thị trường và từ khóa đã xác định, hãy sử dụng tool duckduckgo_market_search để tìm kiếm "
            "thông tin đối thủ, mức giá, nhu cầu người dùng. Sử dụng web_content_scraper để đọc chi tiết các bài viết quan trọng. "
            "Đảm bảo thông tin thu thập đủ đa dạng về giá cả, xu hướng và rủi ro."
        ),
        expected_output="Bản tổng hợp dữ liệu thực tế về đối thủ, giá cả, và các bài viết phân tích ngách.",
        agent=agent,
    )


def create_insight_task(agent: Agent) -> Task:
    """Tạo Task tổng hợp báo cáo chiến lược cho Insight Agent."""
    return Task(
        description=(
            "Tổng hợp toàn bộ thông tin thu thập được và lập một Báo cáo Chiến lược Kinh doanh toàn diện bao gồm các mục:\n"
            "1. Phân tích tiềm năng và góc tiếp cận ngách (Niche Analysis)\n"
            "2. Chiến lược định giá (Suggested Price & Rationale)\n"
            "3. Đánh giá 3-5 rủi ro chính (Risks)\n"
            "4. Bộ từ khóa SEO chiến lược (SEO Keywords)\n"
            "5. Đề xuất 3 prompt gợi ý cho người dùng tạo nội dung marketing (AI Prompts).\n"
            "Trình bày báo cáo rõ ràng, chuyên nghiệp bằng Tiếng Việt."
        ),
        expected_output="Báo cáo chiến lược kinh doanh hoàn chỉnh theo định dạng Markdown sắc nét.",
        agent=agent,
    )
