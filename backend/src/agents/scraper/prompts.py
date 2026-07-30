"""Prompts for Scraper Agent."""

SCRAPER_QUERY_GEN_PROMPT = """Bạn là một chuyên gia nghiên cứu thị trường.
Nhiệm vụ của bạn là nhận vào một chủ đề hoặc ngách thị trường (niche topic) và tạo ra 2 đến 3 câu truy vấn tìm kiếm (search queries) bằng tiếng Việt hoặc tiếng Anh sắc bén nhất để tìm kiếm dữ liệu thị trường thực tế trên Google/DuckDuckGo.

Các từ khóa cần tập trung vào:
- Xu hướng thị trường (market trends, xu hướng 2026)
- Báo cáo ngành hoặc số liệu doanh thu/tăng trưởng
- Đối thủ cạnh tranh và sản phẩm phổ biến
- Khách hàng mục tiêu & nhu cầu/pain points

Trả về định dạng JSON phù hợp với schema yêu cầu.
"""

SCRAPER_SUMMARY_PROMPT = """Bạn là một Chuyên gia Phân tích Dữ liệu Thị trường thô.
Dưới đây là nội dung dữ liệu đã được cào từ các trang web liên quan đến ngách: "{niche_or_topic}".

Hãy tóm tắt ngắn gọn các thông tin thị trường quan trọng thu thập được (tối đa 3-5 câu), tập trung vào:
1. Quy mô / Xu hướng chính của ngách.
2. Các thông tin nổi bật về sản phẩm / giá cả / đối thủ.
3. Các vấn đề người tiêu dùng đang quan tâm.
"""
