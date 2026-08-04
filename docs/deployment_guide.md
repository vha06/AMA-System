# Hướng dẫn Triển khai Cloud Miễn phí (Zero-Cost Deployment Guide)

Tài liệu này hướng dẫn chi tiết từng bước đưa hệ thống **AMA-System** lên môi trường đám mây hoàn toàn miễn phí ($0):
- **Frontend (Next.js)**: Triển khai trên **Vercel**.
- **Backend (FastAPI + CrewAI + Playwright)**: Triển khai trên **Render.com** (hoặc **Koyeb**) thông qua Docker container.

> [!NOTE]
> Hugging Face Spaces gần đây đã chuyển cấu hình Compute (Gradio & Docker Spaces) sang gói trả phí (PRO). Do đó, chúng ta sử dụng **Render.com** hoặc **Koyeb** làm nền tảng thay thế miễn phí $0 tốt nhất để hỗ trợ Docker container.

---

## 1. Chuẩn bị biến môi trường (Environment Variables)

### Biến môi trường Backend (Render / Koyeb Environment Variables)
Chuẩn bị các API key sau để nhập vào danh sách biến môi trường trên Render/Koyeb:
- `GOOGLE_API_KEY`: API key của Google Gemini.
- `SUPABASE_URL`: URL của dự án Supabase.
- `SUPABASE_SERVICE_KEY`: Service role key hoặc anon key của Supabase.
- `UPSTASH_REDIS_REST_URL`: (Nếu sử dụng Upstash Redis) URL REST API từ Upstash Console.
- `UPSTASH_REDIS_REST_TOKEN`: (Nếu sử dụng Upstash Redis) REST Token từ Upstash Console.
- `CORS_ORIGINS`: URL domain của Vercel (ví dụ: `https://ama-system.vercel.app`) hoặc `*`.

---

## 2. Triển khai Backend lên Render.com (Free Web Service)

### Bước 2.1: Đăng ký & Tạo Web Service trên Render
1. Truy cập [Render.com Dashboard](https://dashboard.render.com/) và đăng nhập bằng tài khoản GitHub.
2. Nhấn **New +** -> chọn **Web Service**.
3. Chọn **Build and deploy from a Git repository** và kết nối repo `AMA-System` từ GitHub.

### Bước 2.2: Cấu hình Web Service
1. **Name**: `ama-system-backend`
2. **Region**: Chọn Singapore hoặc gần vị trí của bạn nhất.
3. **Branch**: `main` (hoặc branch chính của bạn).
4. **Root Directory**: `backend` (Rất quan trọng: nhập `backend` để Render trỏ đúng vào Dockerfile của Backend).
5. **Runtime**: Chọn **Docker**.
6. **Instance Type**: Chọn **Free** (512 MB RAM, 0.1 CPU).
7. **Environment Variables**: Thêm tất cả các biến môi trường đã chuẩn bị ở Bước 1.
8. Nhấn **Create Web Service**.

### Bước 2.3: Lấy Public URL của Backend
Sau khi Render build Docker image thành công (mất khoảng 3-5 phút):
1. URL public của API sẽ có dạng: `https://ama-system-backend.onrender.com`
2. Kiểm tra bằng cách mở trình duyệt truy cập: `https://ama-system-backend.onrender.com/health` -> Nhận kết quả `{"status":"ok","service":"ama-backend"}`.

---

## 3. Triển khai Frontend lên Vercel

### Bước 3.1: Kết nối Vercel với GitHub
1. Truy cập [Vercel Dashboard](https://vercel.com) và đăng nhập bằng GitHub.
2. Nhấn **Add New...** -> **Project**.
3. Chọn Repository `AMA-System` từ danh sách GitHub.

### Bước 3.2: Cấu hình Project trên Vercel
1. **Framework Preset**: Chọn **Next.js**.
2. **Root Directory**: Nhấn **Edit** và chọn thư mục `frontend`.
3. **Environment Variables**: Thêm biến môi trường sau:
   - Key: `NEXT_PUBLIC_BACKEND_URL`
   - Value: `https://ama-system-backend.onrender.com` (URL lấy từ Bước 2.3).
4. Nhấn **Deploy**.

---

## 4. Phương án dự phòng: Triển khai Backend lên Koyeb (Nếu muốn 1-click)

Nếu không dùng Render, bạn có thể triển khai trên [Koyeb.com](https://www.koyeb.com/):
1. Đăng ký tài khoản Koyeb miễn phí.
2. Tạo Service -> Chọn **GitHub** -> Kết nối repo `AMA-System`.
3. Chọn Builder: **Docker** -> Root Directory: `/backend`.
4. Nhập các Environment Variables.
5. Koyeb sẽ cấp cho bạn đường link `.koyeb.app`.

---

## 5. Kiểm tra & Nghiệm thu (Verification)

1. **Khởi động lần đầu (Cold Start)**: 
   - Render / Koyeb Free Tier sẽ tự động tạm dừng (sleep) sau 15 phút không có truy cập. Khi mở app Vercel, request đầu tiên có thể mất 30-50 giây để server khởi động lại.
2. **Kiểm tra chức năng**:
   - Mở ứng dụng từ URL `.vercel.app`.
   - Nhập câu hỏi nghiên cứu thị trường.
   - Kiểm tra kết quả hiển thị trên bảng điều khiển và xem luồng SSE streaming truyền dữ liệu thời gian thực từ Render Backend về Vercel Frontend.
