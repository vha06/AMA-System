# ADR-002: Kiến trúc luồng Agent 4 bước tuần tự (Pipeline)

## Status
Accepted

## Date
2026-08-04

## Context
Trong giai đoạn đầu (MVP Phase 1-6) của AMA-System, chúng ta cần một kiến trúc kết nối các Agent (Router, Scraper, GraphRAG, Insight) đảm bảo tính ổn định cao, dễ debug, và có khả năng chạy "chay" (fallback) khi thiếu API Key.

## Decision
Áp dụng mô hình **Đường ống xử lý tuần tự tĩnh (Static Sequential Pipeline)**:
1. `Router Agent`: Phân loại ý định người dùng (hợp lệ/không).
2. `Scraper Agent`: Thu thập dữ liệu từ DuckDuckGo/Web.
3. `GraphRAG Agent`: Chuyển đổi dữ liệu thành Vector/Triplets.
4. `Insight Agent`: Đọc Graph và sinh báo cáo Generative UI.

Tất cả các Agent đều kế thừa lớp base có tích hợp sẵn `_heuristic_fallback()`. Nếu quá trình sinh lỗi (do hết Rate Limit của Gemini hoặc thiếu Key), hệ thống tự động trả về Mock Data để UI không bị sập.

## Alternatives Considered

### CrewAI / AutoGen (Áp dụng ngay từ Giai đoạn 1)
- Pros: Agents tự chủ, tự phân công công việc.
- Cons: Khó kiểm soát luồng dữ liệu ở giai đoạn sớm, dễ bị ảo giác (hallucination) dẫn đến kẹt vòng lặp (infinite loop). Khó thiết lập Fallback Mode tĩnh.
- Rejected: Trì hoãn việc dùng Multi-Agent framework sang Giai đoạn 7, ưu tiên MVP ổn định trước.

## Consequences
- Hệ thống cực kỳ dễ đoán, dễ bảo trì, và không bao giờ crash trên Frontend.
- Tuy nhiên, độ thông minh bị giới hạn. Nếu Scraper tìm sai dữ liệu, Insight vẫn phải phân tích dữ liệu sai đó mà không có cơ chế tự yêu cầu Scraper tìm lại. (Lý do để nâng cấp CrewAI ở GĐ 7).
