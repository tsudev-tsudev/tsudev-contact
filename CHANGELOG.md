# CHANGELOG — tsudev-contact

Mỗi bản phát hành 1 dòng, định dạng: `{version} — {DD/MM/YYYY} — nội dung thay đổi`.
Quy ước đặt tên bản phát hành: `docs/DESIGN_SYSTEM.md` mục 6.

## Chưa phát hành

- Sửa lỗi nút "BẮT ĐẦU CHUYỂN ĐỔI" mất chữ trên Windows (theme `vista` bỏ qua nền của nút ttk) — chuyển sang `tk.Button` dùng màu từ tokens.
- Đoán cột CSV thông minh hơn: `converter.guessHeader` + `FIELD_ALIASES` (Anh/Việt, bỏ dấu, khớp `Phone 1 - Value` kiểu Google Contacts); trước đây trường bắt buộc SĐT luôn phải chọn tay.
- Chạy thử GUI thật trên Windows (Python 3.11): 3 màn hình → chuyển đổi 30 dòng → 20 vCard → cửa sổ xem trước hiển thị đúng, dòng lỗi tô đỏ.
- Chuẩn hóa tên bản phát hành theo `docs/DESIGN_SYSTEM.md` mục 6: `APP_VERSION` 5.2 → `26.8.2001`; `Contacts.spec` chuyển sang gói 1-file, xuất `tsudev-contact_26.8.2001_x64-setup.exe`.
- Thêm `scripts/build-win.ps1`: cài phụ thuộc → chạy test → PyInstaller → đưa sản phẩm vào `release/`.
- Chuẩn hóa repo theo bộ quy ước v1.0.0: khởi tạo git, ignore dữ liệu danh bạ PII, bổ sung `CHANGELOG.md` / `docs/ARCHITECTURE.md` / `.env.example`.
- Tách `contacts.pyw` (455 dòng) thành `src/` theo `docs/PROJECT_STRUCTURE.md`; `contacts.pyw` giữ vai trò điểm khởi chạy mỏng.
- Toàn bộ màu/cỡ chữ/spacing của giao diện lấy từ `tokens/design-tokens.json` qua `src/services/tokens.py` (hết hard-code).
- Sửa 3 lỗi: `sqlite3.Row.get()` làm hỏng hoàn toàn chức năng xuất VCF và cửa sổ xem trước; sai số tham số `_update_progress`; rò rỉ kết nối SQLite. Chi tiết: `docs/ARCHITECTURE.md` mục 6.
- CSDL tạm chuyển sang thư mục temp của người dùng (thư mục cài đặt có thể chỉ-đọc, và file đó chứa PII).
- Thêm `tests/test_csv_to_vcf.py` — 8 test tích hợp luồng CSV → SQLite → vCard.

## Đã phát hành

_Chưa có bản nào phát hành. Bản kế tiếp đã sẵn sàng mang số `26.8.2001` — chỉ chờ chạy thử GUI trên Windows rồi chạy `scripts/build-win.ps1`._
_Các bản build trước 20/08/2026 dùng tên `Contacts.exe` (không theo quy ước)._
