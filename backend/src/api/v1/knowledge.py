from fastapi import APIRouter, HTTPException, status
from src.core.models import KnowledgeAddRequest, KnowledgeQueryRequest, KnowledgeQueryResponse
from src.database.knowledge_db import GraphRAGKnowledgeBase

router = APIRouter(prefix="/knowledge", tags=["GraphRAG Knowledge Base"])
kb = GraphRAGKnowledgeBase()


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
    summary="Thêm dữ liệu thô vào GraphRAG Knowledge Base",
    description="Trích xuất Triplets từ văn bản, lưu vào NetworkX Knowledge Graph và ChromaDB Vector Store.",
)
async def add_knowledge(request: KnowledgeAddRequest):
    try:
        triplets = kb.add_knowledge(request.text)
        return {
            "message": "Đã nạp kiến thức thành công vào GraphRAG.",
            "triplets_extracted": len(triplets),
            "triplets": triplets,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi nạp dữ liệu vào Knowledge Base: {str(e)}",
        )


@router.post(
    "/query",
    response_model=KnowledgeQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Truy vấn GraphRAG Knowledge Base",
    description="Tìm kiếm ngữ nghĩa trên ChromaDB kết hợp duyệt đồ thị NetworkX để trả về bối cảnh ngữ cảnh phong phú.",
)
async def query_knowledge(request: KnowledgeQueryRequest) -> KnowledgeQueryResponse:
    try:
        response = kb.query_knowledge(request.query, top_k=request.top_k)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi truy vấn Knowledge Base: {str(e)}",
        )
