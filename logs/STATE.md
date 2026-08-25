# STATE.md - Trạng thái project (agent đọc đầu phiên, cập nhật cuối phiên)

## Hàng đợi task (làm từ trên xuống)
- [ ] (trống - chủ project giao task mới)

### Gợi ý việc tiếp theo (chưa phải task, cần chủ project duyệt)
- Phát hành bản `26.8.2003` gói các thay đổi đang ở mục "Chưa phát hành" của `CHANGELOG.md`: sửa `APP_VERSION` → đẩy tag `v26.8.2003` → Actions tự build và đính `.exe` vào Release.
- Xóa chứng thư thử nghiệm còn sót trong kho tin cậy của Windows (xem mục "Việc dang dở").
- Kiểm thử GUI chưa phủ: bố cục có vỡ không, hiệu ứng trượt/mờ, `.exe` chạy trên máy sạch - vẫn phải nhìn mắt khi đổi giao diện lớn.
- Muốn hết cảnh báo SmartScreen phải mua chứng thư OV/EV (không có phương án miễn phí tương đương).

- [ ] **QU-STD-1** Di trú `tokens/` sang `.standards/tokens/` (nguồn chân lý duy nhất). Hiện có **4 file mã nguồn** đọc token cục bộ. Đây là thay đổi PHÁ VỠ: `text-muted` đổi giá trị ở cả ba chế độ và có thêm `border-control`. Làm theo CHANGELOG mục 2.0.0 "Hướng dẫn nâng cấp", chạy lại ảnh chụp giao diện.
- [ ] **QU-STD-2** Xóa bản sao quy ước cũ nay đã trùng `.standards/`: docs/DESIGN_SYSTEM.md docs/PROJECT_STRUCTURE.md docs/templates/HANDOVER.md - giữ lại chỉ tạo hai nguồn chân lý.
- [ ] **QU-STD-AUTH** Rà luồng đăng nhập theo `.standards/docs/AUTH_AND_ACCOUNT.md` mục 17. **CHẶN, cần chủ project quyết trước khi làm**: tài liệu mục 1 xếp `tsudev-contact` là **hạng A - web có tài khoản**, nhưng repo này là app desktop Tkinter đóng gói `.exe` bằng PyInstaller, chạy ngoại tuyến, không có tài khoản nào. Theo mô tả trong bảng thì nó là **hạng C**. Làm theo hạng A nghĩa là dựng cả luồng OIDC cho một công cụ chuyển CSV sang vCard. Xem TS-15 ở `tsudev-standards`.
- [ ] **QU-STD-TABLE** Thêm bộ chọn số bản ghi `10/20/50/100/200` (mặc định `10`, góc dưới bên trái) cho cửa sổ xem trước danh bạ. Chuẩn: `.standards/docs/DATA_TABLE.md` mục 12.
- [ ] **QU-STD-BRAND** Bổ sung tài sản nhận diện còn thiếu và siêu dữ liệu nối về `tsudev.com`. Chuẩn: `.standards/docs/BRAND_ASSETS.md` mục 14 và `.standards/docs/ECOSYSTEM_IDENTITY.md` mục 9.
- [ ] **QU-STD-3** Rà chỗ dùng `border-strong` cho viền nút phụ hoặc ô nhập, đổi sang `border-control` (`.standards/docs/DESIGN_SYSTEM.md` mục 1).

## Đang thực hiện
| Task | Agent | Bắt đầu |
|---|---|---|

## Đã hoàn thành (mới nhất trên cùng)
- 20/08/2026 - T14: repo chuyển **public**; Actions hết bị chặn, chạy trọn pipeline xanh (run `32291387041`); sửa 2 lỗi workflow (cache pip thiếu requirements.txt, đối chiếu tag khi chạy tay)
- 20/08/2026 - T13 `8470ceb`: `scripts/sign-win.ps1` ký Authenticode + dấu thời gian miễn phí, `build-win.ps1` thêm `-Sign` và tự ghi `release/SHA256SUMS.txt`
- 20/08/2026 - T12 `f528c3a`: `tests/test_gui_smoke.py` + `scripts/test-gui-win.ps1` tự động hóa kịch bản GUI (5 test, chạy thật trên Windows và trên runner CI); phát hiện & sửa lỗi gọi `root.after` từ thread nền
- 20/08/2026 - T11 `4eed8a5`: cửa sổ xem trước dùng nhãn vCard + cột `Dòng CSV` + chú thích cột CSV nguồn (6 test)
- 20/08/2026 - T10: push `main` lên repo private; tạo Release `v26.8.2002` kèm `.exe` + `SHA256SUMS.txt`; thêm workflow tự build khi đẩy tag
- 20/08/2026 - T9: chủ đề Sáng/Ấm/Tối + `src/services/settings.py` (ghi nhớ lựa chọn), 18/18 test
- 20/08/2026 - T8 `a47aa98`: chạy thử GUI thật trên Windows → phát hiện & sửa 2 lỗi (nút mất chữ, đoán cột CSV)
- 20/08/2026 - Build thật: `release/tsudev-contact_26.8.2002_x64-setup.exe` (18.5 MB), đã chạy thử file .exe
- 20/08/2026 - T7: thêm `scripts/build-win.ps1` (deps → test → PyInstaller → `release/`)
- 20/08/2026 - T6: chuẩn hóa tên phát hành - `APP_VERSION=26.8.2001`, `RELEASE_BASENAME` trong `src/app_info.py`, `Contacts.spec` gói 1-file
- 20/08/2026 - T5: tạo repo private `tsudev-tsudev/tsudev-contact`, push `main` (không file PII nào được theo dõi)
- 20/08/2026 - T3+T4 `b947660`: tách `contacts.pyw` → `src/`, giao diện dùng `tokens/`, thêm 8 test, sửa 3 lỗi
- 20/08/2026 - T2 `332c74d`: thêm CHANGELOG / ARCHITECTURE / .env.example, viết lại README
- 20/08/2026 - T1 `5032a7f`: `git init`, ignore dữ liệu danh bạ PII
- 19/08/2026 - Khởi tạo bộ quy ước v1.0.0

## Quyết định quan trọng
- 20/08/2026 - **Repo đã chuyển PUBLIC** theo yêu cầu chủ project. Hệ quả đã kiểm chứng: GitHub Actions chạy lại bình thường (hết lỗi chặn thanh toán), phút Actions miễn phí không giới hạn, trang Releases ai cũng tải được. Toàn bộ project không dùng dịch vụ trả phí nào.
- 20/08/2026 - **Ký số**: chỉ dùng công cụ miễn phí có sẵn của Windows (`Set-AuthenticodeSignature` + timestamp RFC3161). Chứng thư tự ký KHÔNG gỡ được SmartScreen trên máy khác - chấp nhận, thay bằng đối chiếu `SHA256SUMS.txt`. Không mua chứng thư OV/EV.
- 20/08/2026 - Workflow **không bật `cache: pip`**: repo không có `requirements.txt` (phụ thuộc khai báo trong `scripts/build-win.ps1`); thêm file chỉ để cache là trùng lặp không đáng, repo public nên không cần tiết kiệm phút.
- 20/08/2026 - **tkinter không an toàn đa luồng**: mọi cập nhật UI từ thread nền phải qua `queue.Queue` do main thread rút (`ContactsApp._pumpUiQueue`), tuyệt đối không gọi `root.after` từ thread khác.
- 20/08/2026 - Phát hành qua **GitHub Releases**, tag `v<APP_VERSION>` (ví dụ `v26.8.2002`). Workflow chỉ chạy theo tag để tiết kiệm phút Actions; runner `windows-latest` tính 2x phút.
- 20/08/2026 - Repo giữ **private**: trang Releases chỉ mở được với tài khoản có quyền. Muốn ai cũng tải được thì phải chuyển repo sang public (chủ project quyết định).
- 20/08/2026 - **Cách chạy GUI/build Windows từ WSL**: gọi `powershell.exe` (interop) dùng Python 3.11 sẵn có trên Windows, tạo venv trong `%TEMP%\tsudev-contact-build`. Không cần cài `python3-tk` trong WSL.
- 20/08/2026 - Chủ đề sáng giữ ttk theme `vista` (native đẹp); ấm/tối bắt buộc `clam` vì `vista` bỏ qua màu nền. Nút hành động chính dùng `tk.Button` để chắc chắn đủ tương phản.
- 20/08/2026 - `scripts/build-win.ps1` phải lưu **UTF-8 CÓ BOM**: PowerShell 5.1 đọc .ps1 không BOM theo ANSI → hỏng tiếng Việt, lỗi cú pháp.
- 20/08/2026 - Không thêm trình cài đặt (Inno/NSIS): `Contacts.spec` chuyển sang **gói 1-file**, chính file `.exe` đó là bản `-setup.exe` theo quy ước. Thêm installer chỉ khi cần shortcut/uninstaller.
- 20/08/2026 - `src/app_info.py` là nguồn duy nhất của tên bản phát hành (`RELEASE_BASENAME`); spec và script build đều đọc từ đó. Bản kế tiếp trong ngày chỉ cần tăng `NN`.
- 20/08/2026 - `src/` dùng `snake_case` cho file/thư mục (Python không import được dấu gạch ngang); hàm/biến giữ `camelCase`.
- 20/08/2026 - Logic chuyển đổi tách khỏi tkinter, giao tiếp qua callback → test được không cần màn hình.
- 20/08/2026 - Giao diện đọc thẳng `tokens/design-tokens.json` qua `src/services/tokens.py`; cỡ chữ truyền tkinter dạng số âm = pixel.
- 20/08/2026 - CSDL tạm đặt ở thư mục temp người dùng, không đặt cạnh file thực thi (chỉ-đọc + chứa PII).
- 19/08/2026 - Dùng Inter làm font chuẩn; token là nguồn chân lý duy nhất; region ưu tiên Singapore → Nhật Bản.
