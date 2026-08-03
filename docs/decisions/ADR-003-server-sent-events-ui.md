# ADR-003: Render Generative UI thời gian thực qua Server-Sent Events

## Status
Accepted

## Date
2026-08-04

## Context
Hệ thống AMA-System sinh ra các báo cáo thị trường rất dài (bao gồm Niche, Risks, Pricing, SEO, Prompts). Nếu sử dụng phương pháp HTTP Request-Response thông thường, người dùng sẽ phải nhìn màn hình chờ (loading spinner) vài phút trước khi thấy kết quả.

## Decision
Sử dụng **Server-Sent Events (SSE)** từ FastAPI Backend đẩy dữ liệu liên tục về Next.js Frontend.
Ở Frontend, sử dụng `Vercel AI SDK` (`streamObject` hoặc custom stream reader) kết hợp với công cụ parse JSON liên tục (`json-stream-parser.ts`) để render (vẽ) từng thẻ UI (Generative UI Component) ngay khi dữ liệu của mảng đó vừa được sinh ra.

## Alternatives Considered

### WebSockets
- Pros: Giao tiếp hai chiều, tốc độ cao.
- Cons: Khó cấu hình hơn trên các serverless platform như Vercel; tốn tài nguyên duy trì kết nối cho những task sinh text một chiều.
- Rejected: SSE nhẹ hơn và phù hợp hoàn hảo cho luồng dữ liệu một chiều (LLM -> Client).

### HTTP REST truyền thống
- Pros: Dễ code, chuẩn mực.
- Cons: Trải nghiệm người dùng (UX) cực kỳ tệ khi phải đợi sinh vài nghìn token.
- Rejected: Yêu cầu của hệ thống là một UI hiện đại.

## Consequences
- **UX tuyệt vời:** Người dùng thấy dữ liệu xuất hiện ngay lập tức như đang chat với ChatGPT.
- **Complexity:** Việc parse luồng JSON bị đứt đoạn (streaming JSON) rất phức tạp, đòi hỏi hàm parser vững chắc để không gây crash Frontend khi render cấu trúc lồng nhau.
