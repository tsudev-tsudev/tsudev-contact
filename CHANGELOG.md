# CHANGELOG — tsudev-contact

Mỗi bản phát hành 1 dòng, định dạng: `{version} — {DD/MM/YYYY} — nội dung thay đổi`.
Quy ước đặt tên bản phát hành: `docs/DESIGN_SYSTEM.md` mục 6.

## Chưa phát hành

- Chuẩn hóa repo theo bộ quy ước v1.0.0: khởi tạo git, ignore dữ liệu danh bạ PII, bổ sung `CHANGELOG.md` / `docs/ARCHITECTURE.md` / `.env.example`.
- Tách `contacts.pyw` (455 dòng) thành `src/` theo `docs/PROJECT_STRUCTURE.md`; `contacts.pyw` giữ vai trò điểm khởi chạy mỏng.
- Toàn bộ màu/cỡ chữ/spacing của giao diện lấy từ `tokens/design-tokens.json` qua `src/services/tokens.py` (hết hard-code).
- Sửa 3 lỗi: `sqlite3.Row.get()` làm hỏng hoàn toàn chức năng xuất VCF và cửa sổ xem trước; sai số tham số `_update_progress`; rò rỉ kết nối SQLite. Chi tiết: `docs/ARCHITECTURE.md` mục 6.
- CSDL tạm chuyển sang thư mục temp của người dùng (thư mục cài đặt có thể chỉ-đọc, và file đó chứa PII).
- Thêm `tests/test_csv_to_vcf.py` — 8 test tích hợp luồng CSV → SQLite → vCard.

## Đã phát hành

_Chưa có bản nào phát hành theo quy ước tên `{ten-app}_{YY}.{M}.{DD}{NN}_{arch}-setup.{ext}`._
_Các bản build trước 20/08/2026 dùng tên `Contacts.exe` (không theo quy ước) — xem task chuẩn hóa trong `logs/STATE.md`._
