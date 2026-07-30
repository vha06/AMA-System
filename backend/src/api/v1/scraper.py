from fastapi import APIRouter, HTTPException, status
from src.agents.scraper.schemas import ScraperInput, ScraperOutput
from src.agents.scraper.agent import ScraperAgent

router = APIRouter(prefix="/scraper", tags=["Scraper Agent"])
scraper_agent = ScraperAgent()


@router.post(
    "/scrape",
    response_model=ScraperOutput,
    status_code=status.HTTP_200_OK,
    summary="Cào & Thu thập Dữ liệu Thị trường",
    description="Nhận thông tin ngách từ Router Agent, tự động tìm kiếm trên internet và cào dữ liệu thô phục vụ GraphRAG.",
)
async def scrape_market_data(payload: ScraperInput) -> ScraperOutput:
    try:
        result = await scraper_agent.run(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi thu thập dữ liệu thị trường: {str(e)}",
        )
