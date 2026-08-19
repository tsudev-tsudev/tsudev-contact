# tsudev-contact

Công cụ desktop chuyển danh bạ **CSV → vCard (.vcf)** để nạp vào điện thoại,
kèm cửa sổ xem trước có phân trang.

## Chạy trong 5 phút

```bash
python -m pip install pillow     # dependency duy nhất ngoài thư viện chuẩn
python contacts.pyw              # Windows: bấm đúp contacts.pyw
```

1. **Chọn file CSV** danh bạ (dòng đầu là tên cột, hỗ trợ BOM UTF-8).
2. Ánh xạ cột CSV sang trường vCard — bắt buộc có **Tên** và **SĐT**.
3. Bấm chuyển đổi → file `.vcf` được ghi cạnh file CSV. Xem trước dữ liệu ở menu tương ứng.

## Đóng gói Windows

```bash
python -m pip install pyinstaller
pyinstaller Contacts.spec
```

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
