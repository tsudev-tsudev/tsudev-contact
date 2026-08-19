# PHIẾU BÀN GIAO — Chuẩn hóa repo + tái cấu trúc mã nguồn

- **Mã phiếu**: 20260820-01
- **Từ**: agent-session-20260820 — **Đến**: phiên sau
- **Thời điểm**: 01:35 20/08/2026
- **Trạng thái**: HOÀN THÀNH (còn việc tiếp nối ở mục 2)

## 1. Việc đã làm xong

- **T1** `5032a7f` — `git init` (nhánh `main`), bổ sung `.gitignore`: `*.csv`, `*.vcf` (dữ liệu danh bạ = PII), giữ ngoại lệ `*.example.csv`. Quét mã nguồn: không có secret/API key.
- **T2** `332c74d` — thêm `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `.env.example`; viết lại `README.md` (bản cũ mô tả bộ quy ước, không phải app này).
- **T3+T4** `b947660` — tách `contacts.pyw` (455 dòng) thành `src/`; toàn bộ giao diện lấy giá trị từ `tokens/design-tokens.json`; thêm `tests/test_csv_to_vcf.py` (8/8 pass); `Contacts.spec` đóng gói thêm `tokens/`.
- **T5** — tạo repo **private** `https://github.com/tsudev-tsudev/tsudev-contact`, đã push `main`. Xác minh: không file `*.csv/*.vcf/*.db/.env` nào được theo dõi.
- Dọn thư mục rỗng rác `{docs/templates,tokens,logs/handover}` (brace-expansion hỏng lúc khởi tạo).

## 2. Việc dang dở + bước tiếp theo CỤ THỂ

- [ ] **Chạy thử GUI trên Windows** — bắt buộc trước khi phát hành. WSL hiện không có `tkinter`/`Pillow`/màn hình nên chỉ kiểm được logic + phân tích tĩnh.
      Lệnh: `python -m pip install pillow` rồi `python contacts.pyw`.
      Tiêu chí: 2 màn hình hiệu ứng chạy → cửa sổ chính trượt xuống → chọn CSV → ghép cột → chuyển đổi ra `.vcf` → mở "Xem thử Danh bạ" không lỗi.
- [ ] **Chuẩn hóa tên bản phát hành** (DESIGN_SYSTEM.md mục 6): `Contacts.spec` đang xuất `Contacts.exe`; `src/app_info.py` đang giữ `APP_VERSION = "5.2"`.
      Bản kế tiếp đổi sang `tsudev-contact_{YY}.{M}.{DD}{NN}_x64-setup.exe` + chuỗi version tương ứng, ghi 1 dòng vào `CHANGELOG.md`.
- [ ] **Thêm `scripts/build-win.ps1`** gói lệnh PyInstaller (PROJECT_STRUCTURE.md yêu cầu thư mục `scripts/`).
- [ ] (tùy chọn) Thêm tùy chọn chủ đề `warm`/`dark` — `src/services/tokens.py` đã hỗ trợ, `ContactsApp` mới dùng `light`.

## 3. File liên quan / đang khóa

- Không còn khóa nào. `logs/LOCKS.md` đã trống.

## 4. Yêu cầu gửi agent đang giữ khóa

- Không có.

## 5. Cảnh báo / quyết định quan trọng

- **Bản gốc có 3 lỗi thật, đã sửa** (chi tiết `docs/ARCHITECTURE.md` mục 6). Nặng nhất: `sqlite3.Row` không có `.get()` khiến **chức năng xuất VCF và cửa sổ xem trước chưa bao giờ chạy xong** — mọi lần chuyển đổi đều rơi vào nhánh "Lỗi nghiêm trọng". Hãy đối chiếu với trải nghiệm thực tế của chủ project.
- **Đặt tên trong `src/` dùng `snake_case`** thay vì `kebab-case`: Python không import được tên có dấu gạch ngang (áp dụng ngoại lệ "theo chuẩn ngôn ngữ" của PROJECT_STRUCTURE.md). Hàm/biến vẫn `camelCase`.
- **CSDL tạm đã chuyển** từ thư mục cài đặt sang temp của người dùng (`%TEMP%/tsudev-contact/contacts_data.db`): thư mục cài đặt có thể chỉ-đọc, và file đó chứa PII.
- **`gh` có 2 tài khoản**; phiên này đã `gh auth switch --user tsudev-tsudev`. Kiểm tra tài khoản active trước khi thao tác GitHub.
- Kiểm thử hiện có **chỉ phủ phần logic** (`converter`, `database`); phần tkinter chưa có test.

## 6. Kết quả xử lý

- 20/08/2026 (phiên 20260820b) — **đã xử lý xong toàn bộ mục 2**:
  - Chạy thử GUI trên Windows: dùng Python 3.11 của máy Windows qua interop WSL (`powershell.exe`),
    venv riêng trong `%TEMP%`. Cả 3 màn hình + luồng chuyển đổi + xem trước đều đạt.
    **Phát hiện 2 lỗi thật** (nút chính mất chữ, đoán cột bỏ sót SĐT) — đã sửa, xem `docs/ARCHITECTURE.md` mục 6.1.
  - Chuẩn hóa tên phát hành + `scripts/build-win.ps1`: xong, đã build thật ra
    `release/tsudev-contact_26.8.2002_x64-setup.exe` (18.5 MB) và chạy thử file .exe đó.
  - Chủ đề warm/dark (mục tùy chọn): đã làm, có menu *Giao diện* + ghi nhớ lựa chọn.
- Cảnh báo về `sqlite3.Row` ở mục 5 được xác nhận đúng: sau khi sửa, luồng xuất VCF chạy trọn vẹn
  (30 dòng CSV → 20 vCard hợp lệ, 10 dòng thiếu SĐT bị đánh dấu đỏ).
