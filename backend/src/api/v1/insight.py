import json
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.agents.insight.agent import InsightAgent
from src.database.supabase_db import supabase_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insight", tags=["Strategic Insight Agent"])
insight_agent = InsightAgent()


class InsightStreamRequest(BaseModel):
    topic: str = Field(..., description="Chủ đề hoặc từ khóa phân tích thị trường")
    context_data: str = Field(
        "", description="Dữ liệu ngữ cảnh thu thập từ Scraper hoặc GraphRAG"
    )
    user_id: Optional[str] = Field(None, description="ID người dùng từ Supabase Auth")


@router.post(
    "/stream",
    status_code=status.HTTP_200_OK,
    summary="Stream báo cáo phân tích chiến lược",
    description="Stream trực tiếp các khối văn bản JSON thô (raw JSON chunks) của InsightReport hỗ trợ streamObject từ Vercel AI SDK.",
)
async def stream_insight_report(
    request: InsightStreamRequest,
    x_user_id: Optional[str] = Header(None, alias="x-user-id")
):
    target_user_id = request.user_id or x_user_id or "anonymous"

    async def logging_generator():
        accumulated_text = ""
        try:
            for chunk in insight_agent.stream_insight(
                topic=request.topic, context_data=request.context_data
            ):
                accumulated_text += chunk
                yield chunk

            # Parse JSON or wrap raw text
            results = {"raw_result": accumulated_text}
            try:
                results = json.loads(accumulated_text)
            except Exception:
                pass

            await supabase_db.save_session_log(
                user_id=target_user_id,
                prompt=request.topic,
                results=results,
                status="success",
                source_links=[]
            )
        except Exception as e:
            logger.error(f"Error during insight streaming or session saving: {e}")
            try:
                await supabase_db.save_session_log(
                    user_id=target_user_id,
                    prompt=request.topic,
                    results={"error": str(e)},
                    status="error",
                    source_links=[]
                )
            except Exception:
                pass

    try:
        return StreamingResponse(logging_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi stream báo cáo insight: {str(e)}",
        )
