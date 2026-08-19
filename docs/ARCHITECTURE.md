# ARCHITECTURE.md — Quyết định kiến trúc của repo tsudev-contact

> Ghi 1 lần, các phiên sau tham chiếu đường dẫn này thay vì đọc lại mã nguồn.
> Quy ước chung: `AGENTS.md`, `docs/PROJECT_STRUCTURE.md`, `docs/DESIGN_SYSTEM.md`.

## 1. Mục đích

Công cụ desktop chuyển danh bạ từ **CSV → vCard (.vcf)** để nạp vào điện thoại,
kèm cửa sổ xem trước dữ liệu có phân trang.

## 2. Ngăn xếp công nghệ

| Thành phần | Lựa chọn | Lý do |
|---|---|---|
| GUI | `tkinter` + `ttk` (thư viện chuẩn Python) | Không thêm dependency, đóng gói 1 file .exe nhẹ |
| Ảnh/icon | `Pillow` (`PIL`) | Duy nhất 1 dependency ngoài stdlib |
| Lưu trữ tạm | `sqlite3` (stdlib) → `contacts_data.db` | Xem trước hàng nghìn dòng không nạp hết vào RAM |
| Chạy nền | `threading` | Giữ UI không đơ khi chuyển đổi file lớn |
| Đóng gói | PyInstaller — `Contacts.spec` | `console=False`, nhúng `icon.png` qua `datas` |

## 3. Bố cục mã nguồn

`contacts.pyw` ở gốc chỉ còn là **điểm khởi chạy mỏng** (nạp `sys.path` rồi gọi `src.main.app.main`)
— giữ nguyên để `Contacts.spec` và thói quen bấm đúp file không đổi.

```
src/
├── app_info.py                     # tên app, phiên bản, tác giả — khai báo 1 nơi
├── main/app.py                     # AppLauncher: splash → cửa sổ chính + hiệu ứng trượt
├── features/
│   ├── csv_to_vcf/converter.py     # logic chuyển đổi THUẦN, không import tkinter
│   ├── csv_to_vcf/ui.py            # ContactsApp: chọn file, ghép cột, nhật ký
│   ├── preview/ui.py               # PreviewWindow: treeview + phân trang
│   └── splash/{matrix,system_check}.py
├── services/
│   ├── database.py                 # DatabaseManager (SQLite)
│   └── tokens.py                   # đọc tokens/design-tokens.json → API màu/font/spacing
└── utils/{resource_path,dpi}.py
tests/test_csv_to_vcf.py            # test tích hợp luồng CSV → SQLite → vCard
```

**Quy tắc đặt tên**: thư mục/file theo `snake_case` thay vì `kebab-case` — Python không
import được tên có dấu gạch ngang. Áp dụng ngoại lệ "theo chuẩn ngôn ngữ" của
`docs/PROJECT_STRUCTURE.md`; ngữ nghĩa tên giữ nguyên. Hàm/biến dùng `camelCase` đúng quy ước.

**Ranh giới UI ↔ logic**: `converter.py` không biết gì về tkinter; nó báo tiến trình và lỗi
từng dòng qua callback `onProgress` / `onRowError`. `ui.py` chạy nó trong thread nền và
đẩy mọi cập nhật về main thread qua `_uiCall()` (bọc `root.after`). Nhờ vậy toàn bộ luồng
chuyển đổi test được mà không cần màn hình.

**Giao diện dùng token**: `src/services/tokens.py` đọc thẳng `tokens/design-tokens.json`
(đúng chỉ dẫn trong chính file token). Cỡ chữ truyền cho tkinter dưới dạng **số âm = pixel**
để khớp đơn vị px của token. Màn hình hiệu ứng dùng bảng màu chủ đề `dark`.

## 4. Luồng dữ liệu

```
File CSV người dùng chọn (filedialog)
  → đọc header (encoding utf-8-sig, xử lý BOM)
  → người dùng ánh xạ cột CSV ↔ trường vCard (bắt buộc: Tên, SĐT)
  → thread nền: đọc từng dòng → ghi SQLite (xem trước) → ghi file .vcf
  → log tiến trình + thanh progress trên UI chính
```

## 5. Quyết định & ràng buộc

- **Dữ liệu danh bạ không bao giờ vào git.** `*.csv`, `*.vcf`, `*.db` đã ignore
  (PII: họ tên, số điện thoại, chức vụ cán bộ). Đường dẫn CSV do người dùng chọn
  lúc chạy, **không hard-code** — nên việc ignore không ảnh hưởng ứng dụng.
- **Chạy hoàn toàn cục bộ**: không gọi mạng, không secret, không biến môi trường
  (xem `.env.example`). Không phát sinh chi phí hạ tầng.
- **Chỉ 1 dependency ngoài stdlib** (`Pillow`) — giữ nguyên tắc "thư viện nhẹ" của AGENTS.md mục 4.

## 6. Lỗi đã sửa khi tái cấu trúc (20/08/2026)

Ba lỗi tồn tại trong bản 1 file, phát hiện khi tách module:

1. **`sqlite3.Row` không có `.get()`** — `contact.get('email')` trong luồng xuất VCF ném
   `AttributeError` ngay liên hệ đầu tiên, rơi vào `except` và báo "Lỗi nghiêm trọng"
   → **chức năng xuất VCF không bao giờ chạy xong**. `PreviewWindow` mắc đúng lỗi này.
   Đã đổi sang truy cập bằng khóa (`contact['email'] or ''`), có test chặn hồi quy.
2. **Sai số tham số** — `_update_progress(value, text)` được gọi với 3 tham số ở nhánh
   hoàn tất và nhánh lỗi → `TypeError`, thanh tiến trình không bao giờ chốt 100%.
3. **Rò rỉ kết nối SQLite** — `with sqlite3.connect(...)` chỉ commit/rollback, không đóng
   kết nối. Đã bọc `contextlib.closing`.

Ngoài ra, CSDL tạm chuyển từ thư mục cài đặt (`resourcePath`) sang thư mục temp của người
dùng: thư mục cài đặt có thể chỉ-đọc (Program Files), và file đó chứa PII.

## 7. Nợ kỹ thuật còn lại

1. `Contacts.spec` đặt tên đầu ra `Contacts.exe`, chưa theo quy ước
   `tsudev-contact_{YY}.{M}.{DD}{NN}_x64-setup.exe` (DESIGN_SYSTEM.md mục 6);
   chuỗi phiên bản trong `src/app_info.py` vẫn là `5.2` — đổi khi phát hành bản kế tiếp.
2. Chưa có script build trong `scripts/`.
3. Chưa chạy thử GUI sau tái cấu trúc: môi trường phát triển hiện tại (WSL) không có
   `tkinter`/`Pillow`/màn hình. Đã kiểm bằng test logic (8/8) + pyflakes sạch;
   **cần chạy thử trên Windows trước khi phát hành**.
4. Ứng dụng mới chỉ dùng chủ đề `light`; token đã sẵn `warm`/`dark` nếu muốn thêm tùy chọn.
