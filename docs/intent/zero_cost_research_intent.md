# Intent Document: AMA-System Zero-Cost Research Stack

## Summary
Dự án Phân tích thị trường tự động (AMA-System) được định hướng phát triển thành một dự án nghiên cứu cá nhân dài hạn, áp dụng các công nghệ AI hàng đầu (Multi-Agent, GraphRAG, Generative UI) với ràng buộc bắt buộc: **Chi phí duy trì và vận hành hoàn toàn bằng $0 (Zero-Cost Architecture)**.

## Key Details
- **Outcome:** Hệ thống tự động phân tích thị trường từ Prompt -> Generative UI Dashboard.
- **User:** Cá nhân nghiên cứu, tự học và thử nghiệm kỹ thuật AI/Fullstack.
- **Success Criteria:** Hệ thống chạy trơn tru end-to-end với chi phí $0.

## Zero-Cost Tech Stack Constraints
- **LLM Engine:** Gemini 3.1 Pro (Free Tier API).
- **Scraper Agent:** Open-source thuần (`Playwright` / `DuckDuckGo Search API` / `BeautifulSoup`) thay vì Apify.
- **GraphRAG:** `ChromaDB` (Vector) + `NetworkX` (In-Memory Graph Database).
- **Primary DB & Cache:** Supabase Free Tier (PostgreSQL) + Upstash Redis Free Tier.
- **Frontend Hosting:** Vercel Free Tier.
- **Backend Environment:** Local dev (`uv` package manager) / Render Free Tier nếu cần deploy API.

## Out of Scope
- Không sử dụng bất kỳ dịch vụ Cloud Scraping trả phí nào (như Apify, BrightData).
- Không dựng server Neo4j trả phí (dùng NetworkX trước).
- Không thuê máy chủ/VPS trả phí.
