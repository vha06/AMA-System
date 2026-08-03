# ADR-001: Lựa chọn Tech Stack $0 (Zero-Cost Research Stack)

## Status
Accepted

## Date
2026-08-04

## Context
Dự án AMA-System (Automated Market Analysis System) được định vị là một hệ thống nghiên cứu cá nhân dài hạn. Ngân sách dành cho cơ sở hạ tầng và API là $0. Tuy nhiên, hệ thống đòi hỏi khả năng xử lý LLM mạnh mẽ, thu thập dữ liệu web và lưu trữ vector/graph.

## Decision
Sử dụng bộ công nghệ hoàn toàn miễn phí (Free Tier/Open Source):
- **LLM Engine:** Gemini 3.5 Flash (Google AI Studio Free Tier).
- **Trình cào dữ liệu (Scraper):** Playwright & DuckDuckGo Search (chạy local/mã nguồn mở).
- **Cơ sở dữ liệu:** 
  - Cache: Upstash Redis (Free Tier).
  - Primary DB & Auth: Supabase PostgreSQL (Free Tier).
  - Graph/Vector: NetworkX (In-memory) + ChromaDB (Local).
- **Hosting:** Vercel (Frontend Next.js) + Local/Render (Backend FastAPI).

## Alternatives Considered

### OpenAI (GPT-4o) & Anthropic (Claude 3.5 Sonnet)
- Pros: Khả năng suy luận đỉnh cao, hệ sinh thái phong phú.
- Cons: Trả phí theo Token, dễ dàng gây tốn kém khi chạy khối lượng lớn dữ liệu phân tích thị trường.
- Rejected: Phá vỡ nguyên tắc Zero-Cost.

### Apify (Cloud Scraping)
- Pros: Dễ dàng cấu hình, IP rotation có sẵn.
- Cons: Giới hạn tính phí cao.
- Rejected: Playwright (local) đáp ứng đủ nhu cầu mà không tốn chi phí.

### Neo4j (Graph Database)
- Pros: Database đồ thị mạnh mẽ, trực quan.
- Cons: Bản AuraDB Free có giới hạn node rất nhỏ, dễ vượt ngưỡng khi cào dữ liệu lớn.
- Rejected: Sử dụng NetworkX lưu trong bộ nhớ kết hợp ChromaDB (local) là đủ cho GraphRAG cá nhân.

## Consequences
- **Tích cực:** Dự án có thể vận hành vô thời hạn mà không lo hóa đơn đám mây.
- **Tiêu cực:** Các Free Tier (đặc biệt là Supabase và Vercel) có giới hạn băng thông và cold start. Playwright local yêu cầu nhiều tài nguyên CPU/RAM khi chạy.
