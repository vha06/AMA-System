# ADR-008: Kiến trúc Triển khai Đám mây Zero-Cost (Zero-Cost Deployment Architecture)

## Status
Accepted

## Date
2026-08-05

## Context
Dự án AMA-System cần một môi trường triển khai thực tế (public online) cho một nhóm nhỏ người dùng thử (Beta Testers) nhằm thu thập đánh giá.
Yêu cầu cốt lõi là **không tốn bất kỳ chi phí duy trì nào ($0 Cost)**.
Tuy nhiên, hệ thống lại có những đặc thù đòi hỏi cấu hình máy chủ cao:
- Chạy môi trường Python (FastAPI).
- Chạy hệ thống Đa tác tử (CrewAI) và LlamaIndex Property Graph.
- Chạy Headless Chromium bằng Playwright để Scrape dữ liệu mạng xã hội và e-commerce.

Hầu hết các nền tảng miễn phí hiện nay đều giới hạn tài nguyên khắt khe (ví dụ: 512MB RAM), điều này dễ dẫn đến lỗi Out Of Memory (OOM) khi Chromium và AI cùng chạy.

## Decision
Sử dụng mô hình triển khai phân tán tận dụng các Free Tier hiện có sau khi đánh giá lại chính sách của các nhà cung cấp:

1.  **Frontend (Next.js): Vercel (Free Tier)**
    - Lựa chọn tiêu chuẩn, zero-config, hỗ trợ Server-Sent Events (SSE) tối ưu, cấp sẵn domain HTTPS.
2.  **Backend (FastAPI + Playwright): Render.com hoặc Koyeb (Free Docker Tier)**
    - Triển khai trực tiếp qua `Dockerfile` để cài đặt Chromium.
    - *Lưu ý: Hugging Face Spaces trước đây là lựa chọn hàng đầu nhờ 16GB RAM, tuy nhiên gần đây nền tảng này đã thu phí cho Docker/Compute Spaces nên không còn phù hợp với tiêu chí $0.*
    - Chấp nhận trade-off: Máy chủ Render miễn phí sẽ tự động "ngủ đông" (Sleep) sau 15 phút không hoạt động, yêu cầu "Cold Start" ~30-50 giây cho request đầu tiên.
3.  **Database & Auth: Supabase (Free Tier)**
    - Toàn bộ dữ liệu phiên (Session Logs) và xác thực người dùng được giữ an toàn tại Supabase PostgreSQL.
4.  **Cache: Upstash Redis (Free Tier)**
    - Dùng để lưu trữ tạm các kết quả trung gian hoặc rate-limiting, đảm bảo tính liên tục của hệ thống.

## Alternatives Considered

### Hugging Face Spaces (Docker Space)
- Pros: Khá mạnh (16GB RAM) cho AI.
- Cons: Hiện tại đã bắt buộc trả phí cho các môi trường chạy Compute/Docker, chỉ cho phép Static spaces miễn phí.
- Rejected: Vi phạm ràng buộc $0 Cost.

### Self-Hosted (VPS Oracle Cloud Free Tier)
- Pros: Khá mạnh (lên tới 24GB RAM ARM).
- Cons: Khó đăng ký (tỉ lệ từ chối thẻ ảo cao), quản trị hệ thống phức tạp, tốn công thiết lập HTTPS và pipeline CI/CD.
- Rejected: Quá tải về mặt vận hành (operations) cho một dự án nghiên cứu nhỏ gọn.

## Consequences
- Đảm bảo 100% mục tiêu Zero-Cost.
- Người dùng thử sẽ phải chịu một chút độ trễ (delay) trong lần truy cập đầu tiên do Cold Start của Backend từ Render/Koyeb.
- Nguy cơ chạm trần bộ nhớ (OOM) 512MB: Nếu Chromium hoặc mô hình AI ngốn quá nhiều RAM, hệ thống có thể bị crash ngầm. Cần tối ưu code scraping và dọn dẹp bộ nhớ liên tục trong backend.
