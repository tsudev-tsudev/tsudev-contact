# PHIẾU BÀN GIAO — Chạy thử GUI trên Windows, phát hành 26.8.2002, chủ đề Sáng/Ấm/Tối

- **Mã phiếu**: 20260820-02
- **Từ**: agent-session-20260820b — **Đến**: phiên sau
- **Thời điểm**: 01:30 20/08/2026
- **Trạng thái**: HOÀN THÀNH (hàng đợi task đã cạn)

## 1. Việc đã làm xong

- **T6** `44e9350` — chuẩn hóa tên phát hành: `src/app_info.py` thêm `APP_ARCH`, `RELEASE_BASENAME`;
  `Contacts.spec` chuyển **gói 1-file**, tên file lấy từ `RELEASE_BASENAME`.
- **T7** `44e9350` — `scripts/build-win.ps1`: kiểm tra Python → (tùy chọn) cài deps → chạy test →
  PyInstaller → chuyển sản phẩm vào `release/`. Cờ `-SkipDeps`, `-KeepBuild`.
- **T8** `a47aa98` — chạy thử GUI thật trên Windows, phát hiện và sửa **2 lỗi**:
  1. nút "BẮT ĐẦU CHUYỂN ĐỔI" mất chữ (ttk theme `vista` bỏ qua `-background`) → dùng `tk.Button`;
  2. đoán cột CSV bỏ sót trường bắt buộc SĐT → `converter.guessHeader` + `FIELD_ALIASES` (Anh/Việt,
     bỏ dấu, khớp `Phone 1 - Value` kiểu Google Contacts). Chi tiết: `docs/ARCHITECTURE.md` mục 6.1.
- **T9** — chủ đề **Sáng / Ấm / Tối**: menu *Giao diện*, đổi ngay lúc chạy, ghi nhớ qua
  `src/services/settings.py` (`settings.json` trong thư mục tạm của app; `database.py` dùng chung
  `appDataDir()`). Kiểm thử: 18/18 test + chụp màn hình cả 3 chủ đề trên Windows.
- **Phát hành**: `release/tsudev-contact_26.8.2002_x64-setup.exe` (18.5 MB) — đã chạy thử chính file
  .exe đó (cửa sổ chính lên đúng, tiêu đề `v26.8.2002`). `release/` nằm trong `.gitignore`.

- **T10** — đẩy `main` lên repo private và dựng phần phát hành trên GitHub:
  Release [`v26.8.2002`](https://github.com/tsudev-tsudev/tsudev-contact/releases/tag/v26.8.2002)
  kèm `.exe` (19.4 MB) + `SHA256SUMS.txt`; thêm `.github/workflows/build-release-win.yml` để lần sau
  chỉ cần đẩy tag `v<APP_VERSION>` là tự build và đính file vào Release.

## 2. Việc dang dở + bước tiếp theo CỤ THỂ

- Không còn việc dang dở. Hàng đợi trong `logs/STATE.md` đã cạn — chờ chủ project giao task mới.
- Gợi ý (chưa phải task, xem `logs/STATE.md`): ký số .exe; tự động hóa kiểm thử GUI;
  cột cửa sổ xem trước đang hiện tên cột CSV thay vì nhãn vCard.

## 3. File liên quan / đang khóa

- Không còn khóa nào. `logs/LOCKS.md` trống. Cây làm việc sạch, mọi thay đổi đã commit.

## 4. Yêu cầu gửi agent đang giữ khóa

- Không có.

## 5. Cảnh báo / quyết định quan trọng

- **Chạy GUI/build Windows từ WSL**: không cần cài `python3-tk` trong WSL. Dùng interop:
  `powershell.exe -NoProfile -Command "cd $env:TEMP\tsudev-contact-build; ..."`, copy mã nguồn bằng
  `git archive HEAD | tar -x -C /mnt/c/Users/<user>/AppData/Local/Temp/tsudev-contact-build`,
  tạo venv `python -m venv .venv` rồi cài `pillow pyinstaller`. Máy này có Python 3.11.9 cài sẵn cho người dùng Windows hiện tại
  (`%LOCALAPPDATA%\Programs\Python\Python311`).
- **`scripts/build-win.ps1` phải giữ UTF-8 CÓ BOM** — PowerShell 5.1 đọc .ps1 không BOM theo ANSI,
  chữ tiếng Việt hỏng và script không chạy được. Đừng "dọn" BOM này.
- **Quy tắc giao diện Windows**: ttk theme `vista` chỉ tôn trọng `foreground`/`font`, **bỏ qua
  `background`**. Muốn đổi nền: dùng `tk.Button`/`tk.Text` hoặc chuyển theme `clam` (chủ đề ấm/tối
  đang làm vậy). Thanh cuộn Tk cổ điển do Windows vẽ native, không đổi màu được → dùng `ttk.Scrollbar`.
- **Đánh số bản phát hành**: `26.8.2001` là build nội bộ, không phát hành; bản chính thức trong ngày
  là `26.8.2002`. Bản kế tiếp cùng ngày → `26.8.2003` (chỉ sửa `APP_VERSION` trong `src/app_info.py`).
- **Workflow phát hành chưa chạy được**: `gh workflow run build-release-win.yml` → job thất bại sau 2
  giây, annotation: *"The job was not started because recent account payments have failed or your
  spending limit needs to be increased"*. Đây là vấn đề thanh toán của tài khoản GitHub, **không phải
  lỗi workflow** (job đã được tạo nên YAML hợp lệ). Bản 26.8.2002 vì vậy được build tại máy và đẩy lên
  Release bằng `gh release create`.
- **Repo đang private** → trang Releases chỉ mở được bằng tài khoản có quyền. Muốn người ngoài tải
  được phải chuyển repo sang public (mã nguồn đã sạch PII, nhưng đây là quyết định của chủ project).
- **Tài khoản `gh`**: phiên này đã `gh auth switch --user tsudev-tsudev`. Máy có 2 tài khoản, luôn
  kiểm tra `gh api user --jq .login` trước khi thao tác GitHub.
- **Không có ảnh chụp màn hình nào được giữ lại** — thư mục làm việc tạm trên Windows đã xóa sạch
  (ảnh chụp có thể lọt nội dung cửa sổ khác của chủ máy).

## 6. Kết quả xử lý (agent nhận điền sau khi thực hiện)

- (phiên sau điền)
