from typing import Optional
from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.agents.crew.crew_orchestrator import HierarchicalMarketCrew
from src.database.supabase_db import supabase_db

router = APIRouter(prefix="/crew", tags=["CrewAI Multi-Agent System"])


class CrewRequest(BaseModel):
    query: str = Field(..., description="Truy vấn nghiên cứu thị trường của người dùng.")
    user_id: Optional[str] = Field(None, description="ID người dùng từ Supabase Auth")


@router.post(
    "/stream",
    status_code=status.HTTP_200_OK,
    summary="Stream báo cáo phân tích thị trường từ Đội ngũ Đa tác tử CrewAI",
    description="Kích hoạt Hierarchical CrewAI (Router -> Scraper -> Insight với Manager Agent), stream toàn bộ tiến trình phản biện và kết quả về client.",
)
async def stream_crew_analysis(
    request: CrewRequest,
    x_user_id: Optional[str] = Header(None, alias="x-user-id")
):
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Truy vấn không được để rỗng.",
        )

    user_id = request.user_id or x_user_id or "anonymous"

    try:
        crew_runner = HierarchicalMarketCrew(query=request.query.strip())
        return StreamingResponse(
            crew_runner.stream_analysis(user_id=user_id),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi khởi chạy CrewAI: {str(e)}",
        )


@router.get(
    "/sessions",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách các phiên tìm kiếm của người dùng",
)
async def get_user_sessions(
    user_id: Optional[str] = None,
    x_user_id: Optional[str] = Header(None, alias="x-user-id")
):
    target_user_id = user_id or x_user_id
    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiếu user_id.",
        )
    sessions = await supabase_db.get_user_sessions(user_id=target_user_id)
    return {"sessions": sessions}


@router.get(
    "/sessions/{session_id}",
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết một phiên tìm kiếm",
)
async def get_session_by_id(session_id: str):
    session = await supabase_db.get_session_by_id(session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên làm việc.",
        )
    return session

