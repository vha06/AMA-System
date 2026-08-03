# ADR-005: Nâng cấp GraphRAG với LlamaIndex Property Graph

## Status
Accepted

## Date
2026-08-04

## Context
MVP GraphRAG (Phase 5) được xây dựng thủ công bằng NetworkX kết hợp với thuật toán tách Triplets cơ bản. Hạn chế: Khó scale, truy vấn (query) còn thủ công, và thiếu khả năng nhúng meta-data phức tạp vào các Node.

## Decision
Sử dụng **LlamaIndex Property Graph** để thay thế lõi NetworkX thuần.
Property Graphs cho phép gắn thuộc tính động vào cả Node và Edge, giúp truy vấn bằng Cypher hoặc tích hợp sẵn Vector Search trên cùng một không gian đồ thị.

## Alternatives Considered

### LangChain GraphQA
- Pros: Gắn chặt vào hệ sinh thái LangChain.
- Cons: Phụ thuộc vào Neo4j server, vi phạm Zero-Cost.
- Rejected: LlamaIndex cung cấp tính năng Property Graph có thể chạy In-Memory hoặc với các Storage miễn phí linh hoạt hơn.

## Consequences
- Hệ thống chiết xuất tri thức tự động, thông minh hơn, lấy ra các insight ngách ẩn sâu trong dữ liệu thị trường (như mối quan hệ Đối thủ - Giá bán - Đánh giá người dùng).
- Có learning curve lớn khi cấu hình LlamaIndex.
