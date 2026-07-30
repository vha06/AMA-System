from pydantic import BaseModel, Field


class PricingStrategy(BaseModel):
    """Chiến lược giá đề xuất và giải thích logic."""

    suggested_price: str = Field(
        description="Mức giá đề xuất hoặc khoảng giá phù hợp cho thị trường/ngách"
    )
    rationale: str = Field(
        description="Lý giải nguyên nhân, căn cứ lựa chọn mức giá này"
    )


class InsightReport(BaseModel):
    """Báo cáo phân tích thị trường & chiến lược kinh doanh từ Insight Agent."""

    niche_analysis: str = Field(
        description="Phân tích ngách thị trường, tiềm năng và tiềm năng phát triển"
    )
    pricing: PricingStrategy = Field(
        description="Chiến lược định giá sản phẩm/dịch vụ"
    )
    risks: list[str] = Field(
        description="Danh sách các rủi ro, thách thức chính cần lưu ý"
    )
    seo_keywords: list[str] = Field(
        description="Danh sách từ khóa SEO/thị trường tiềm năng để tối ưu bài viết hoặc quảng cáo"
    )
    ai_prompts: list[str] = Field(
        description="Danh sách các câu lệnh gợi ý (prompts) để người dùng tiếp tục khai thác các công cụ AI khác"
    )
