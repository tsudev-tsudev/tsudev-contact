# STATE.md — Trạng thái project (agent đọc đầu phiên, cập nhật cuối phiên)

## Hàng đợi task (làm từ trên xuống)
- [ ] (trống — chủ project giao task mới)

### Gợi ý việc tiếp theo (chưa phải task, cần chủ project duyệt)
- Quyết định để repo private (chỉ mình tải) hay chuyển public (ai cũng tải được từ trang Releases, và Actions chạy miễn phí không giới hạn).
- Xử lý cảnh báo thanh toán ở *Settings → Billing & plans* nếu muốn dùng GitHub Actions cho repo private.
- Ký số bản .exe để tránh cảnh báo SmartScreen trên máy khác.
- Tự động hóa kiểm thử GUI (kịch bản ở `docs/ARCHITECTURE.md` mục 8) — hiện chạy tay.
- Cột trong cửa sổ xem trước đang hiển thị tên cột CSV, chưa phải nhãn vCard.

## Đang thực hiện
| Task | Agent | Bắt đầu |
|---|---|---|

## Đã hoàn thành (mới nhất trên cùng)
- 20/08/2026 — T10: push `main` lên repo private; tạo Release `v26.8.2002` kèm `.exe` + `SHA256SUMS.txt`; thêm workflow tự build khi đẩy tag
- 20/08/2026 — T9: chủ đề Sáng/Ấm/Tối + `src/services/settings.py` (ghi nhớ lựa chọn), 18/18 test
- 20/08/2026 — T8 `a47aa98`: chạy thử GUI thật trên Windows → phát hiện & sửa 2 lỗi (nút mất chữ, đoán cột CSV)
- 20/08/2026 — Build thật: `release/tsudev-contact_26.8.2002_x64-setup.exe` (18.5 MB), đã chạy thử file .exe
- 20/08/2026 — T7: thêm `scripts/build-win.ps1` (deps → test → PyInstaller → `release/`)
- 20/08/2026 — T6: chuẩn hóa tên phát hành — `APP_VERSION=26.8.2001`, `RELEASE_BASENAME` trong `src/app_info.py`, `Contacts.spec` gói 1-file
- 20/08/2026 — T5: tạo repo private `tsudev-tsudev/tsudev-contact`, push `main` (không file PII nào được theo dõi)
- 20/08/2026 — T3+T4 `b947660`: tách `contacts.pyw` → `src/`, giao diện dùng `tokens/`, thêm 8 test, sửa 3 lỗi
- 20/08/2026 — T2 `332c74d`: thêm CHANGELOG / ARCHITECTURE / .env.example, viết lại README
- 20/08/2026 — T1 `5032a7f`: `git init`, ignore dữ liệu danh bạ PII
- 19/08/2026 — Khởi tạo bộ quy ước v1.0.0

## Quyết định quan trọng
- 20/08/2026 — **GitHub Actions của tài khoản đang bị chặn vì thanh toán** (job dừng sau 2 giây: "recent account payments have failed or your spending limit needs to be increased"). Workflow đã đúng cú pháp (job được tạo); trước mắt phát hành bằng `scripts/build-win.ps1` + `gh release create` trên máy Windows. Actions miễn phí không giới hạn nếu repo chuyển public.
- 20/08/2026 — Phát hành qua **GitHub Releases**, tag `v<APP_VERSION>` (ví dụ `v26.8.2002`). Workflow chỉ chạy theo tag để tiết kiệm phút Actions; runner `windows-latest` tính 2x phút.
- 20/08/2026 — Repo giữ **private**: trang Releases chỉ mở được với tài khoản có quyền. Muốn ai cũng tải được thì phải chuyển repo sang public (chủ project quyết định).
- 20/08/2026 — **Cách chạy GUI/build Windows từ WSL**: gọi `powershell.exe` (interop) dùng Python 3.11 sẵn có trên Windows, tạo venv trong `%TEMP%\tsudev-contact-build`. Không cần cài `python3-tk` trong WSL.
- 20/08/2026 — Chủ đề sáng giữ ttk theme `vista` (native đẹp); ấm/tối bắt buộc `clam` vì `vista` bỏ qua màu nền. Nút hành động chính dùng `tk.Button` để chắc chắn đủ tương phản.
- 20/08/2026 — `scripts/build-win.ps1` phải lưu **UTF-8 CÓ BOM**: PowerShell 5.1 đọc .ps1 không BOM theo ANSI → hỏng tiếng Việt, lỗi cú pháp.
- 20/08/2026 — Không thêm trình cài đặt (Inno/NSIS): `Contacts.spec` chuyển sang **gói 1-file**, chính file `.exe` đó là bản `-setup.exe` theo quy ước. Thêm installer chỉ khi cần shortcut/uninstaller.
- 20/08/2026 — `src/app_info.py` là nguồn duy nhất của tên bản phát hành (`RELEASE_BASENAME`); spec và script build đều đọc từ đó. Bản kế tiếp trong ngày chỉ cần tăng `NN`.
- 20/08/2026 — `src/` dùng `snake_case` cho file/thư mục (Python không import được dấu gạch ngang); hàm/biến giữ `camelCase`.
- 20/08/2026 — Logic chuyển đổi tách khỏi tkinter, giao tiếp qua callback → test được không cần màn hình.
- 20/08/2026 — Giao diện đọc thẳng `tokens/design-tokens.json` qua `src/services/tokens.py`; cỡ chữ truyền tkinter dạng số âm = pixel.
- 20/08/2026 — CSDL tạm đặt ở thư mục temp người dùng, không đặt cạnh file thực thi (chỉ-đọc + chứa PII).
- 19/08/2026 — Dùng Inter làm font chuẩn; token là nguồn chân lý duy nhất; region ưu tiên Singapore → Nhật Bản.
