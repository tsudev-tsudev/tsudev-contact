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

## 3. Bố cục mã nguồn hiện tại (`contacts.pyw`, 455 dòng)

Toàn bộ nằm trong **một file ở gốc repo** — chưa theo `docs/PROJECT_STRUCTURE.md`.

| Vùng | Dòng | Trách nhiệm |
|---|---|---|
| `resource_path()` | 26 | Giải đường dẫn tài nguyên khi chạy từ bundle PyInstaller |
| `DatabaseManager` | 35–82 | Tạo/ghi/đếm/phân trang SQLite (`contacts_data.db`) |
| `SystemCheckWindow`, `MatrixWindow` | 84–143 | Màn hình khởi động hiệu ứng |
| `ContactsApp` | 145–350 | Cửa sổ chính: chọn file, ánh xạ cột, chạy chuyển đổi, log tiến trình |
| `PreviewWindow` | 352–415 | Treeview xem trước + điều khiển phân trang |
| khối khởi động | 417+ | Chuỗi màn hình: matrix → system check → app chính |

**Kế hoạch tách** (task T3 trong `logs/STATE.md`):
`src/main/` (khởi động) · `src/features/csv-to-vcf/` · `src/features/preview/` ·
`src/services/database.py` · `src/utils/resource-path.py`.

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

## 6. Nợ kỹ thuật đã biết

1. Mã nguồn 1 file 455 dòng ở gốc, chưa có `src/` → T3.
2. Màu/cỡ chữ hard-code trong UI (ví dụ `#00ff41` ở hiệu ứng matrix), chưa dùng `tokens/` → T4.
3. `Contacts.spec` đặt tên đầu ra `Contacts.exe`, chưa theo quy ước
   `tsudev-contact_{YY}.{M}.{DD}{NN}_x64-setup.exe` (DESIGN_SYSTEM.md mục 6).
4. Chưa có `tests/`, chưa có script build trong `scripts/`.
