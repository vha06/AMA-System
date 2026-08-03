# ADR-007: Tích hợp Supabase làm Primary DB và Authentication

## Status
Accepted

## Date
2026-08-04

## Context
Dự án cần một cơ sở dữ liệu để lưu trữ vĩnh viễn (Persistent Storage) lịch sử tìm kiếm và các báo cáo (Session Logs), cũng như quản lý người dùng (Authentication) mà không tốn chi phí duy trì máy chủ.

## Decision
Sử dụng **Supabase (Free Tier)**. Nó cung cấp PostgreSQL, Row Level Security (RLS), và Auth API tích hợp sẵn.

## Alternatives Considered

### Firebase
- Pros: Auth mạnh, NoSQL dễ dùng.
- Cons: Data model của AMA-System (Người dùng -> Truy vấn -> Báo cáo) mang tính quan hệ (Relational) rất cao. Firebase (NoSQL) sẽ khó query phức tạp sau này.
- Rejected.

### MongoDB Atlas (Free Tier)
- Pros: Phổ biến, lưu JSON dễ.
- Cons: Không tích hợp sẵn Auth mạnh mẽ và RLS như Supabase.
- Rejected.

## Consequences
- Hệ thống sẽ có tính năng đăng nhập, đăng ký và xem lại báo cáo cũ.
- Database Schema cần được định nghĩa rõ ràng với SQLAlchemy (Python) và kết nối an toàn. Bắt buộc phải bảo mật SUPABASE_KEY.
