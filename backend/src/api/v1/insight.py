from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.agents.insight.agent import InsightAgent

router = APIRouter(prefix="/insight", tags=["Strategic Insight Agent"])
insight_agent = InsightAgent()


class InsightStreamRequest(BaseModel):
    topic: str = Field(..., description="Chủ đề hoặc từ khóa phân tích thị trường")
    context_data: str = Field(
        "", description="Dữ liệu ngữ cảnh thu thập từ Scraper hoặc GraphRAG"
    )


@router.post(
    "/stream",
    status_code=status.HTTP_200_OK,
    summary="Stream báo cáo phân tích chiến lược",
    description="Stream trực tiếp các khối văn bản JSON thô (raw JSON chunks) của InsightReport hỗ trợ streamObject từ Vercel AI SDK.",
)
async def stream_insight_report(request: InsightStreamRequest):
    try:
        generator = insight_agent.stream_insight(
            topic=request.topic, context_data=request.context_data
        )
        return StreamingResponse(generator, media_type="text/plain")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi stream báo cáo insight: {str(e)}",
        )
