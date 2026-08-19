# STATE.md — Trạng thái project (agent đọc đầu phiên, cập nhật cuối phiên)

## Hàng đợi task (làm từ trên xuống)
- [ ] Chạy thử GUI trên Windows sau tái cấu trúc (bắt buộc trước khi phát hành) — xem phiếu 20260820-01 mục 2
- [ ] Chuẩn hóa tên bản phát hành + chuỗi version theo DESIGN_SYSTEM.md mục 6 (`Contacts.spec`, `src/app_info.py`)
- [ ] Thêm `scripts/build-win.ps1` gói lệnh PyInstaller
- [ ] (tùy chọn) Thêm tùy chọn chủ đề warm/dark cho giao diện

## Đang thực hiện
| Task | Agent | Bắt đầu |
|---|---|---|

## Đã hoàn thành (mới nhất trên cùng)
- 20/08/2026 — T5: tạo repo private `tsudev-tsudev/tsudev-contact`, push `main` (không file PII nào được theo dõi)
- 20/08/2026 — T3+T4 `b947660`: tách `contacts.pyw` → `src/`, giao diện dùng `tokens/`, thêm 8 test, sửa 3 lỗi
- 20/08/2026 — T2 `332c74d`: thêm CHANGELOG / ARCHITECTURE / .env.example, viết lại README
- 20/08/2026 — T1 `5032a7f`: `git init`, ignore dữ liệu danh bạ PII
- 19/08/2026 — Khởi tạo bộ quy ước v1.0.0

## Quyết định quan trọng
- 20/08/2026 — `src/` dùng `snake_case` cho file/thư mục (Python không import được dấu gạch ngang); hàm/biến giữ `camelCase`.
- 20/08/2026 — Logic chuyển đổi tách khỏi tkinter, giao tiếp qua callback → test được không cần màn hình.
- 20/08/2026 — Giao diện đọc thẳng `tokens/design-tokens.json` qua `src/services/tokens.py`; cỡ chữ truyền tkinter dạng số âm = pixel.
- 20/08/2026 — CSDL tạm đặt ở thư mục temp người dùng, không đặt cạnh file thực thi (chỉ-đọc + chứa PII).
- 19/08/2026 — Dùng Inter làm font chuẩn; token là nguồn chân lý duy nhất; region ưu tiên Singapore → Nhật Bản.
