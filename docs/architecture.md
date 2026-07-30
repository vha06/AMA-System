# Kiến trúc Hệ thống: Phân tích Thị trường Tự động (AMA-System)

## Tổng quan
Hệ thống thu thập, phân tích và đưa ra đề xuất chiến lược kinh doanh dựa trên GraphRAG, Multi-Agent (CrewAI), và LlamaIndex.

## Kiến trúc 3 tầng
1. **Frontend:** Next.js (App Router), Tailwind CSS, Vercel AI SDK. Deploy trên Vercel.
2. **Backend:** Python, FastAPI, LlamaIndex, CrewAI, `uv`. Phân luồng tác vụ bằng Router Agent.
3. **Database:**
   - **Primary:** Supabase (PostgreSQL) - User, Sessions.
   - **Vector-GraphRAG:** ChromaDB (Vector) + NetworkX (Graph).
   - **Cache:** Upstash Redis.

## Luồng hoạt động (Workflow)
1. User Input -> Router Agent (Phân luồng)
2. Valid Query -> Cache Check
3. Cache Miss -> Scraper Agent (Apify/TikTok)
4. Dữ liệu thô -> GraphRAG Processing (Chroma + NetworkX)
5. Strategic Insight Agent -> Tạo Niche, Pricing, AI Prompts
6. Generative UI Rendering (Frontend)
