from fastapi import APIRouter, HTTPException, status
from src.agents.router.schemas import AnalysisRequest, RouterDecision
from src.agents.router.agent import RouterAgent
from src.database.cache_db import cache

router = APIRouter(prefix="/router", tags=["Router Agent"])
router_agent = RouterAgent()


@router.post(
    "/analyze",
    response_model=RouterDecision,
    status_code=status.HTTP_200_OK,
    summary="Phân tích & Phân luồng Truy vấn Người dùng",
    description="Gửi truy vấn từ người dùng đến Router Agent kết nối Gemini 3.1 Pro API để nhận diện intent và thông tin ngữ cảnh.",
)
async def analyze_user_query(request: AnalysisRequest) -> RouterDecision:
    try:
        # Check cache
        cached_decision = await cache.get_router_decision(request.query)
        if cached_decision:
            return cached_decision
            
        decision = router_agent.analyze_query(request.query)
        
        # Save to cache
        await cache.set_router_decision(request.query, decision)
        
        return decision
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi phân luồng truy vấn: {str(e)}",
        )
