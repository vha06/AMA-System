# ADR-006: Scraping nâng cao vượt Anti-Bot với Playwright Stealth

## Status
Accepted

## Date
2026-08-04

## Context
DuckDuckGo Search và BeautifulSoup chỉ đáp ứng được việc cào dữ liệu từ các trang web tĩnh (Static HTML). Các sàn thương mại điện tử (Amazon, Shopee) hoặc MXH (TikTok) sử dụng JavaScript Rendering và kỹ thuật Anti-Bot rất mạnh.

## Decision
Sử dụng **Playwright** kết hợp với thư viện **playwright-stealth** để mô phỏng trình duyệt thật (Headless Browser Scraping) cho Phase 7.3.
CrewAI Scraper Agent sẽ gọi tool này khi phát hiện mục tiêu cần cào là các trang web khó nhằn.

## Alternatives Considered

### Selenium
- Pros: Cổ điển, nhiều tài liệu.
- Cons: Chậm, cũ, khó cài đặt ẩn danh hơn so với hệ sinh thái Playwright hiện tại.
- Rejected: Playwright nhanh và hiện đại hơn.

### Third-party APIs (Zyte, BrightData, Apify)
- Pros: Khỏi lo anti-bot, IP proxy có sẵn.
- Cons: Tốn phí.
- Rejected: Zero-Cost stack.

## Consequences
- Mở khóa khả năng thu thập dữ liệu sâu trên toàn bộ Internet.
- Yêu cầu môi trường chạy phải cài đặt sẵn browser binaries (có thể làm phình to kích thước Docker image hoặc tốn RAM khi chạy cục bộ).
