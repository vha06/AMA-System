# ADR-004: Tích hợp Khung điều phối Đa tác tử (CrewAI)

## Status
Accepted

## Date
2026-08-04

## Context
Sau khi hoàn thiện MVP (GĐ 1-6) với luồng Pipeline tĩnh (ADR-002), hạn chế lớn nhất là thiếu tính linh hoạt: Agents không thể tự giao tiếp hay sửa lỗi cho nhau. Chúng ta cần một hệ thống nơi các chuyên gia (Router, Scraper, Insight) tự lập kế hoạch và phản biện.

## Decision
Sử dụng **CrewAI** làm khung điều phối (Orchestration Framework) tại Giai đoạn 7.1.
CrewAI sẽ quản lý các Agents, giao phó các Task và cung cấp các Tools (như Playwright Scraper) cho chúng tự do sử dụng.

## Alternatives Considered

### Microsoft AutoGen
- Pros: Giao tiếp hội thoại (conversational) đa tác tử mạnh mẽ.
- Cons: Phù hợp với lập trình và thực thi code hơn là phân tích quy trình nghiệp vụ. Hơi phức tạp trong việc đóng gói output thành Structured JSON để đẩy về Frontend.
- Rejected: CrewAI tập trung vào Role-based và Task-based (Giao việc theo vai trò) - phù hợp hoàn hảo với nghiệp vụ phân tích thị trường.

### LangChain / LangGraph
- Pros: Hệ sinh thái cực lớn, Graph linh hoạt.
- Cons: LangGraph có learning curve rất dốc và tốn nhiều boilerplate code.
- Rejected: CrewAI bọc sẵn các khái niệm này một cách thân thiện hơn.

## Consequences
- Hệ thống thông minh hơn rất nhiều, có khả năng tự sửa lỗi (Self-Correction).
- Cần viết lại toàn bộ thư mục `src/agents/` để tương thích với class `Agent` và `Task` của CrewAI.
- Chi phí token có thể tăng do các Agent hội thoại ngầm với nhau trước khi ra kết quả cuối (cần kiểm soát bằng Token Limit).
