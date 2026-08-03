# Tài liệu API (API Documentation) - AMA-System

Hệ thống AMA-System cung cấp các Endpoints phục vụ xử lý luồng nghiệp vụ Phân tích thị trường tự động. Tất cả API đều sử dụng base URL `/api/v1/`.

## 1. Phân tích ngữ nghĩa người dùng (Router)
- **Endpoint:** `POST /api/v1/router/analyze`
- **Mô tả:** Đánh giá tính hợp lệ của câu hỏi đầu vào (có phải là phân tích thị trường hay không).
- **Request Body:**
  ```json
  {
    "query": "Phân tích thị trường áo thun Halloween năm 2026"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "is_valid": true,
    "intent": "market_analysis",
    "confidence": 0.95
  }
  ```

## 2. Thu thập dữ liệu (Scraper)
- **Endpoint:** `POST /api/v1/scraper/scrape`
- **Mô tả:** Cào dữ liệu theo từ khóa tìm kiếm (Dùng DuckDuckGo hoặc Playwright Stealth).
- **Request Body:**
  ```json
  {
    "query": "Halloween T-shirt trends 2026",
    "depth": "deep"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "raw_data": "[...text content...]",
    "sources": ["url1", "url2"]
  }
  ```

## 3. Quản lý Tri thức (GraphRAG)
- **Endpoint:** `POST /api/v1/knowledge/ingest`
- **Mô tả:** Nhận dữ liệu thô, chiết xuất và lưu trữ vào LlamaIndex Property Graph.
- **Request Body:**
  ```json
  {
    "text": "Dữ liệu cào được từ bước Scraper...",
    "topic": "Halloween T-shirt"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "status": "success",
    "nodes_added": 12,
    "edges_added": 15
  }
  ```

## 4. Trích xuất Báo cáo (Insight Streaming)
- **Endpoint:** `POST /api/v1/insight/stream`
- **Mô tả:** Endpoint quan trọng nhất. Query GraphRAG và sinh JSON Streaming (Server-Sent Events) đẩy về UI.
- **Request Body:**
  ```json
  {
    "query": "Phân tích thị trường áo thun Halloween"
  }
  ```
- **Response (200 OK - text/event-stream):**
  *(Stream dạng JSON object chứa các mảng Niche, Pricing, Risks, Prompts, SEO)*
  ```text
  data: {"niche_ideas": [{"title": "Áo phát quang", "score": 8}]}
  data: {"pricing_strategies": [{"tier": "Premium", "price": 29.99}]}
  ...
  ```

## 5. (Mới) Điều phối Đa tác tử (CrewAI Run)
- **Endpoint:** `POST /api/v1/crew/run`
- **Mô tả:** Kích hoạt CrewAI điều khiển tự động toàn bộ 4 Agents giao tiếp với nhau mà không cần gọi tuần tự các API trên.
- **Request Body:**
  ```json
  {
    "task": "Nghiên cứu đối thủ cạnh tranh bán áo thun ngách Gothic Halloween"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "status": "completed",
    "final_report": "..."
  }
  ```
