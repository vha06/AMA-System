# 🚀 AMA-System (Automated Market Analysis System)

**Hệ thống Phân tích Thị trường Tự động** - Một dự án nghiên cứu cá nhân xây dựng kiến trúc **Zero-Cost Research Stack**. 
Hệ thống nhận đầu vào là một Prompt từ người dùng, tự động đi thu thập dữ liệu (Scraping), đưa vào Đồ thị Tri thức (GraphRAG) và cuối cùng xuất ra một báo cáo phân tích chiến lược dưới dạng giao diện **Generative UI**.

---

## ✨ Các Tính Năng Cốt Lõi (Hiện tại)

- **🧠 Multi-Agent Architecture:** Sử dụng hệ thống đa tác tử (Router Agent -> Scraper Agent -> GraphRAG -> Insight Agent) để xử lý logic từ đầu đến cuối một cách tự động.
- **⚡ Generative UI Dashboard:** Giao diện Next.js hiện đại, hiển thị kết quả phân tích theo thời gian thực (Server-Sent Events) bao gồm 5 khối thông tin chiến lược:
  1. Đề xuất ngách thị trường tiềm năng.
  2. Khoảng giá tối ưu cho sản phẩm.
  3. Đánh giá rủi ro và điểm nghẽn.
  4. Câu lệnh (AI Prompts) hỗ trợ sinh ảnh sản phẩm (Midjourney/DALL-E).
  5. Bộ từ khóa chuẩn SEO.
- **🛡️ Safe Fallback / Mock Mode:** Hệ thống tự động chuyển sang chế độ sử dụng dữ liệu giả định (Heuristic Mock Data) nếu không được cấp API Key, cho phép bạn trải nghiệm luồng giao diện 100% mượt mà mà không lo bị lỗi.
- **🗃️ Caching Layer:** Tích hợp Upstash Redis để lưu trữ tạm các truy vấn lặp lại, tối ưu tốc độ phản hồi.

---

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)

### Backend
- **Framework:** Python / FastAPI
- **LLM Engine:** Gemini 3.1 Pro (qua `google-genai` SDK)
- **Cơ sở dữ liệu Knowledge:** ChromaDB (Vector) + NetworkX (Graph)
- **Caching:** Redis (Upstash)
- **Trình quản lý gói:** `uv` (Nhanh & Hiện đại)

### Frontend
- **Framework:** Next.js 15+ (App Router)
- **Ngôn ngữ:** TypeScript
- **Styling:** Tailwind CSS
- **Luồng dữ liệu:** Server-Sent Events (SSE) với Custom JSON Stream Parser.

---

## ⚙️ Hướng Dẫn Khởi Chạy Demo

### 1. Chuẩn bị Môi trường
Dự án được thiết kế chạy mượt mà ngay cả khi không có tài khoản API (Fallback Mode).
Tuy nhiên, để chạy AI thật, bạn cần copy file `.env.example` thành `.env` trong thư mục `backend/` và điền Key:
```env
GEMINI_API_KEY=your_actual_gemini_key_here
GEMINI_MODEL=gemini-3.1-pro
```

### 2. Khởi động Backend (Cổng 8000)
Mở một cửa sổ Terminal (PowerShell hoặc CMD) và chạy:
```bash
cd backend
uv run uvicorn main:app --reload --port 8000
```
- API Docs (Swagger): `http://localhost:8000/docs`

### 3. Khởi động Frontend (Cổng 3000)
Mở cửa sổ Terminal thứ hai và chạy:
```bash
cd frontend
npm install
npm run dev
```
- Giao diện người dùng: `http://localhost:3000`

---

## 🧭 Hướng Nghiên Cứu Tiếp Theo (Phase 7)
Dự án được định hướng phát triển dài hạn với các mục tiêu nâng cấp sắp tới:
1. **CrewAI:** Xây dựng khung điều phối đa tác tử thông minh hơn thay vì chạy tĩnh.
2. **LlamaIndex Property Graph:** Nâng cấp GraphRAG thành công cụ trích xuất tri thức mạnh mẽ.
3. **Advanced Playwright Scraper:** Vượt anti-bot, lấy dữ liệu mạng xã hội và E-commerce lớn (TikTok, Amazon).
4. **Supabase Auth:** Tích hợp xác thực tài khoản và lưu lịch sử các phiên phân tích.

*(Chi tiết danh sách tác vụ nằm trong file `docs/task.md`)*
