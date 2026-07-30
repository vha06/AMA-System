from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    MARKET_RESEARCH = "MARKET_RESEARCH"
    GENERAL_QA = "GENERAL_QA"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class AnalysisRequest(BaseModel):
    query: str = Field(..., description="Yêu cầu hoặc câu hỏi từ người dùng")
    session_id: Optional[str] = Field(None, description="Mã phiên làm việc (nếu có)")


class RouterDecision(BaseModel):
    intent: IntentType = Field(
        ...,
        description="Ý định chính của yêu cầu: MARKET_RESEARCH, GENERAL_QA, hoặc OUT_OF_SCOPE",
    )
    confidence: float = Field(
        ..., description="Mức độ tin tưởng của quyết định phân luồng (0.0 đến 1.0)"
    )
    niche_or_topic: Optional[str] = Field(
        None, description="Ngách thị trường, sản phẩm hoặc chủ đề kinh doanh trích xuất được"
    )
    target_audience: Optional[str] = Field(
        None, description="Đối tượng khách hàng mục tiêu trích xuất được"
    )
    target_platforms: List[str] = Field(
        default_factory=list,
        description="Danh sách nền tảng truyền thông/thương mại liên quan (như TikTok, Shopee, Facebook, Google, YouTube)",
    )
    reasoning: str = Field(..., description="Giải thích ngắn gọn lý do đưa ra phân luồng")
    clarification_needed: Optional[str] = Field(
        None, description="Cần hỏi lại thông tin gì nếu câu hỏi quá ngắn hoặc thiếu ngữ cảnh"
    )
