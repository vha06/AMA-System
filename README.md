# 🚀 AMA-System (Automated Market Analysis System)

**Hệ thống Phân tích Thị trường Tự động** - Một dự án nghiên cứu cá nhân xây dựng kiến trúc **Zero-Cost Research Stack**. 
Hệ thống nhận đầu vào là một Prompt từ người dùng, tự động đi thu thập dữ liệu (Scraping), đưa vào Đồ thị Tri thức (GraphRAG) và cuối cùng xuất ra một báo cáo phân tích chiến lược dưới dạng giao diện **Generative UI**.

---

## ✨ Các Tính Năng Cốt Lõi (Đã hoàn thiện)

- **🧠 Multi-Agent Architecture (CrewAI):** Tích hợp khung điều phối đa tác tử thông minh. Thay vì chạy tĩnh, các tác tử tự giao tiếp, chia nhỏ nhiệm vụ phân tích thị trường, scrape web và báo cáo.
- **⚡ Generative UI Dashboard:** Giao diện Next.js hiện đại, hiển thị kết quả phân tích theo thời gian thực (Server-Sent Events) bao gồm 5 khối thông tin chiến lược:
  1. Đề xuất ngách thị trường tiềm năng.
  2. Khoảng giá tối ưu cho sản phẩm.
  3. Đánh giá rủi ro và điểm nghẽn.
  4. Câu lệnh (AI Prompts) hỗ trợ sinh ảnh sản phẩm (Midjourney/DALL-E).
  5. Bộ từ khóa chuẩn SEO.
- **🕸️ Đồ thị Tri thức (LlamaIndex):** Nâng cấp GraphRAG với Property Graph, kết hợp sức mạnh biểu diễn linh hoạt của đồ thị và tốc độ truy xuất của LlamaIndex.
- **🕵️ Cào dữ liệu tàng hình (Playwright Stealth):** Thu thập dữ liệu mạnh mẽ, cho phép vượt qua rào cản Anti-bot từ các trang thương mại điện tử lớn.
- **🔐 Quản lý Phiên & Xác Thực (Supabase):** Theo dõi lịch sử phân tích và xác thực người dùng theo thời gian thực (Database + Auth).
- **🛡️ Safe Fallback / Mock Mode:** Hệ thống tự động chuyển sang chế độ sử dụng dữ liệu giả định nếu không được cấp API Key, cho phép trải nghiệm 100% mượt mà.

---

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)

### Backend
- **Framework:** Python / FastAPI
- **LLM Engine:** Gemini 3.5 Flash (Nhanh, chi phí bằng $0)
- **Orchestration:** CrewAI (Multi-Agent Framework)
- **Knowledge Base:** LlamaIndex Property Graph + ChromaDB
- **Scraping:** Playwright + Stealth Plugin
- **Trình quản lý gói:** `uv` (Nhanh & Hiện đại)

### Database & Auth
- **Primary DB / Auth:** Supabase (PostgreSQL, RLS)
- **Caching:** Redis (Upstash)

### Frontend
- **Framework:** Next.js 15+ (App Router)
- **Ngôn ngữ:** TypeScript
- **Styling:** Tailwind CSS
- **Luồng dữ liệu:** Server-Sent Events (SSE) với Custom JSON Stream Parser

---

## ⚙️ Hướng Dẫn Khởi Chạy Demo

### 1. Chuẩn bị Môi trường
Dự án được thiết kế chạy mượt mà ngay cả khi không có tài khoản API (Fallback Mode).
Tuy nhiên, để chạy đầy đủ chức năng AI và Database, bạn cần copy file `.env.example` thành `.env` trong thư mục `backend/` và điền Key:
```env
GEMINI_API_KEY=your_actual_gemini_key_here
GEMINI_MODEL=gemini-3.5-flash

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 2. Khởi động Backend (Cổng 8000)
Mở một cửa sổ Terminal (PowerShell hoặc CMD) và chạy:
```bash
cd backend
uv run playwright install chromium
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

## 📚 Hồ Sơ Quyết Định Kiến Trúc (ADRs) & Tài Liệu API
Để hiểu sâu hơn về lý do lựa chọn các công nghệ (Gemini 3.5, Supabase, CrewAI, LlamaIndex), vui lòng xem:
- [Hồ sơ Quyết định Kiến trúc (ADR)](docs/decisions/)
- [Tài liệu API Hệ thống](docs/api.md)

*(Chi tiết danh sách tiến độ các tác vụ tổng quan nằm trong file `docs/task.md`)*
