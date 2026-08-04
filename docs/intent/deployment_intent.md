# Mục tiêu Triển khai Đám mây (Cloud Deployment Intent)

## Tóm tắt Yêu cầu (Đã xác nhận)
- **Outcome:** Đưa toàn bộ hệ thống AMA-System (cả Frontend Next.js và Backend FastAPI + Playwright thực) lên môi trường cloud online.
- **User:** Một nhóm nhỏ người dùng thử (Beta testers).
- **Why now:** Thu thập đánh giá thực tế từ người khác.
- **Success:** Tester có thể truy cập qua một đường link public, nhập câu hỏi và nhận được báo cáo phân tích từ AI với luồng cào dữ liệu thực tế.
- **Constraint:** Chi phí $0 (Zero-Cost). Chấp nhận việc server bị "ngủ đông" và có độ trễ khởi động.
- **Out of scope:** Máy chủ hoạt động 24/7, chịu tải cao, tên miền tùy chỉnh đắt đỏ, scaling phức tạp.

---

## Kiến trúc Triển khai Đề xuất ($0 Cost)

Cập nhật chiến lược triển khai sau khi Hugging Face Spaces thay đổi chính sách (chỉ cho phép Static Spaces miễn phí, Compute/Docker tính phí):

### 1. Frontend (Next.js) -> Vercel (Free Tier)
- **Lý do:** Vercel là "nhà đẻ" của Next.js, cấu hình zero-config.
- **Ưu điểm:** Băng thông rộng, tự động build từ GitHub, hỗ trợ kết nối Server-Sent Events (SSE) để truyền data thời gian thực mượt mà, cung cấp sẵn sub-domain HTTPS miễn phí (`.vercel.app`).

### 2. Backend (FastAPI + CrewAI + Playwright) -> Render.com (hoặc Koyeb) Free Docker Tier
- **Lý do:** Đã được kiểm chứng hỗ trợ triển khai trực tiếp từ `Dockerfile` trên repo GitHub.
- **Cách hoạt động:** Render build từ `Dockerfile` trong thư mục `/backend`, tự động liên kết biến môi trường `$PORT` và cài đặt Playwright Chromium.
- **Ràng buộc (chấp nhận được):** Máy chủ miễn phí sẽ tự động "ngủ đông" (Sleep) sau 15 phút không có traffic, mất khoảng 30-50 giây để khởi động lại ở request đầu tiên.

### 3. Database & Auth -> Supabase (Free Tier)
- **Lý do:** Dự án đã tích hợp sẵn Supabase. Free Tier cung cấp đủ không gian (500MB DB) để lưu hàng ngàn bản báo cáo (Session Logs) và quản lý người dùng mà không cần lo lắng về việc mất dữ liệu khi Backend bị reset.

### 4. Cache & Queue -> Upstash Redis (Free Tier)
- **Lý do:** Lưu cache tạm thời cho các query lặp lại, tiết kiệm thời gian chạy CrewAI. Giới hạn 10.000 request/ngày (quá dư dả cho nhóm Beta tester).

---

## Các bước thực hiện
1. Tạo thư mục cấu hình Docker (`Dockerfile`, `.dockerignore`) cho Backend chuẩn bị đẩy lên Render / Koyeb (đã hoàn thành).
2. Thiết lập Vercel configuration cho Frontend trong `next.config.ts` (đã hoàn thành).
3. Viết kịch bản triển khai (Deployment Guide) step-by-step cho quá trình đưa code lên Git, kết nối Vercel và Render.com (đã cập nhật tại `docs/deployment_guide.md`).
