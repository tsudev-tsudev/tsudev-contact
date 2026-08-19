# tsudev-contact

Công cụ desktop chuyển danh bạ **CSV → vCard (.vcf)** để nạp vào điện thoại,
kèm cửa sổ xem trước có phân trang.

## Tải bản cài đặt (người dùng cuối)

[**Trang phát hành → Releases**](https://github.com/tsudev-tsudev/tsudev-contact/releases/latest)
→ tải `tsudev-contact_{version}_x64-setup.exe` trong mục *Assets*, bấm đúp để chạy.
File chạy độc lập, **không cần cài Python**. Lần đầu SmartScreen có thể cảnh báo (chưa ký số):
*More info → Run anyway*. Đối chiếu `SHA256SUMS.txt` nếu cần kiểm tra toàn vẹn.

> Repo đang ở chế độ **private**: chỉ tài khoản GitHub được cấp quyền mới mở được link trên.

## Chạy từ mã nguồn (lập trình viên)

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

## Phát hành một bản mới

1. Sửa `APP_VERSION` trong `src/app_info.py` theo `{YY}.{M}.{DD}{NN}` (tăng `NN` nếu cùng ngày).
2. Ghi thay đổi vào `CHANGELOG.md`, commit.
3. `git tag v<APP_VERSION> && git push origin v<APP_VERSION>`.

Workflow `.github/workflows/build-release-win.yml` sẽ chạy trên `windows-latest`: đối chiếu tag với
`APP_VERSION`, chạy test, gọi `scripts/build-win.ps1`, tính SHA256 và đính `.exe` vào Release của tag đó.
Chỉ chạy khi có tag (không chạy mỗi lần push) để tiết kiệm phút Actions của gói miễn phí.

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
