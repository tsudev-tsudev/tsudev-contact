# tsudev-contact

Công cụ desktop chuyển danh bạ **CSV → vCard (.vcf)** để nạp vào điện thoại,
kèm cửa sổ xem trước có phân trang.

## Chạy trong 5 phút

Yêu cầu **Python ≥ 3.8** (dùng toán tử `:=`) kèm `tkinter`. Đã kiểm trên Python 3.14.

```bash
python -m pip install pillow     # dependency duy nhất ngoài thư viện chuẩn
python contacts.pyw              # Windows: bấm đúp contacts.pyw
```

1. **Chọn file CSV** danh bạ (dòng đầu là tên cột, hỗ trợ BOM UTF-8).
2. Ánh xạ cột CSV sang trường vCard — bắt buộc có **Tên** và **SĐT**.
3. Bấm chuyển đổi → file `.vcf` được ghi cạnh file CSV. Xem trước dữ liệu ở menu tương ứng.
4. Menu **Giao diện** đổi chủ đề Sáng / Ấm / Tối; lựa chọn được ghi nhớ cho lần mở sau.

## Chạy test

```bash
python -m unittest discover -s tests    # không cần tkinter/Pillow
```

## Đóng gói Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-win.ps1
```

Script tự cài phụ thuộc, chạy test, gọi PyInstaller và đặt sản phẩm vào `release/` với tên
theo `docs/DESIGN_SYSTEM.md` mục 6 (ví dụ `tsudev-contact_26.8.2002_x64-setup.exe`).
Tên file lấy từ `RELEASE_BASENAME` trong `src/app_info.py` — mỗi bản mới tăng 2 số cuối.

## Lưu ý dữ liệu

File danh bạ thật (`*.csv`, `*.vcf`, `*.db`) chứa **thông tin cá nhân** và đã được
`.gitignore` chặn — không commit chúng vào repo trong mọi trường hợp.

## Tài liệu

| File | Nội dung |
|---|---|
| `AGENTS.md` | Quy ước bắt buộc — đọc đầu MỌI phiên làm việc |
| `docs/ARCHITECTURE.md` | Kiến trúc, luồng dữ liệu, nợ kỹ thuật của repo này |
| `docs/DESIGN_SYSTEM.md` | Hệ màu, typography, quy ước tên bản phát hành |
| `docs/PROJECT_STRUCTURE.md` | Cây thư mục chuẩn + quy tắc đặt tên |
| `tokens/` | Nguồn chân lý duy nhất cho màu/cỡ chữ/spacing |
| `logs/` | `STATE.md` hàng đợi task · `LOCKS.md` khóa file · `handover/` phiếu bàn giao |
| `CHANGELOG.md` | Mỗi bản phát hành 1 dòng |
