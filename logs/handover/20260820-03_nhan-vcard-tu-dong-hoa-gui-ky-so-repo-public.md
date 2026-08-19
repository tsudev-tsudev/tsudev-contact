# PHIẾU BÀN GIAO — Nhãn vCard, tự động hóa kiểm thử GUI, ký số miễn phí, repo public

- **Mã phiếu**: 20260820-03
- **Từ**: agent-session-20260820c — **Đến**: phiên sau
- **Thời điểm**: 03:05 20/08/2026
- **Trạng thái**: HOÀN THÀNH (hàng đợi task đã cạn)

## 1. Việc đã làm xong

- **T11** `4eed8a5` — cửa sổ xem trước hiển thị **nhãn vCard** (Tên, SĐT, Email…) thay tên cột CSV.
  Định nghĩa cột tách sang `src/features/preview/columns.py` (thuần, không tkinter → test được
  trong WSL); thêm cột `Dòng CSV` và một dòng chú thích `nhãn ← cột CSV nguồn` ngay trên bảng.
  6 test: `tests/test_preview_columns.py`.
- **T12** `f528c3a` — `tests/test_gui_smoke.py` (5 test) tự động hóa trọn kịch bản
  `docs/ARCHITECTURE.md` mục 8; chạy bằng `scripts/test-gui-win.ps1` (thêm `-GuiOnly`).
  Test gọi thẳng handler widget + tự quay vòng lặp bằng `update()`, đổi `tempfile.tempdir` để
  không đụng dữ liệu thật, thay `messagebox` bằng bản ghi nhận. Máy không có màn hình → tự skip.
  **Lỗi thật do test phát hiện**: `_uiCall` gọi `root.after` từ thread chuyển đổi →
  `RuntimeError: main thread is not in main loop`. Đã chuyển sang `queue.Queue` +
  `_pumpUiQueue` (30ms) và `after_cancel` khi cửa sổ gốc bị hủy. Ghi ở `ARCHITECTURE.md` 6.2.
- **T13** `8470ceb` — `scripts/sign-win.ps1`: ký Authenticode + dấu thời gian RFC3161 bằng công cụ
  có sẵn của Windows (miễn phí), hỗ trợ `-PfxPath` / `-Thumbprint` / `-SelfSigned` / `-TrustLocally`.
  Mật khẩu `.pfx` chỉ qua `$env:SIGN_PFX_PASSWORD` hoặc hỏi kín. `build-win.ps1` thêm cờ `-Sign` và
  tự ghi `release/SHA256SUMS.txt` (đã bỏ bước tính hash trùng trong workflow).
- **T14** — repo `tsudev-tsudev/tsudev-contact` đã chuyển **public**. Actions hết bị chặn thanh toán,
  chạy trọn pipeline xanh: [run 32291387041](https://github.com/tsudev-tsudev/tsudev-contact/actions/runs/32291387041).
  Sửa 2 lỗi workflow lộ ra khi chạy thật: `cache: pip` đòi `requirements.txt` (đã bỏ cache);
  bước đối chiếu tag luôn hỏng khi chạy tay (thêm `if: github.ref_type == 'tag'`).
- Kiểm thử: 29/29 test — WSL (24 chạy + 5 skip), Windows 3.11.9 (29 chạy thật), runner
  `windows-latest` (29 chạy thật, có cả 5 test GUI).

## 2. Việc dang dở + bước tiếp theo CỤ THỂ

- [ ] **Xóa chứng thư thử nghiệm còn sót trên máy Windows của chủ project.** Phiên này thử
  `sign-win.ps1 -SelfSigned -TrustLocally` nên có chứng thư tự ký
  `848CD641BE4144B5991B2D8F2B9AA8BF197EA57D` (`CN=tsudev (self-signed…)`) nằm trong
  `Cert:\CurrentUser\Root`. Chứng thư trong `Cert:\CurrentUser\My` đã xóa; bản trong Root
  **xóa được nhưng Windows bắt bấm xác nhận trên màn hình**, agent không tự bấm được. Chủ project
  chạy lệnh sau rồi bấm **Yes** ở hộp thoại:
  ```powershell
  Get-ChildItem Cert:\CurrentUser\Root | Where-Object { $_.Subject -like '*tsudev (self-signed*' } |
    ForEach-Object { Remove-Item -Path $_.PSPath -Force }
  ```
  Không nguy hiểm (chứng thư không còn khóa riêng nên không ký được nữa), nhưng nên dọn.
- [ ] Chưa phát hành bản mới. Mọi thay đổi trên đang nằm ở mục **Chưa phát hành** của
  `CHANGELOG.md`. Muốn phát hành: sửa `APP_VERSION` → `26.8.2003` trong `src/app_info.py`,
  chuyển các dòng đó xuống mục `26.8.2003`, commit, rồi
  `git tag v26.8.2003 && git push origin v26.8.2003` — Actions tự build và đính `.exe` +
  `SHA256SUMS.txt` vào Release (đã kiểm chứng pipeline chạy được).

## 3. File liên quan / đang khóa

- Không còn khóa nào. `logs/LOCKS.md` trống, cây làm việc sạch, `main` đã đẩy lên GitHub.

## 4. Yêu cầu gửi agent đang giữ khóa

- Không có.

## 5. Cảnh báo / quyết định quan trọng

- **Repo đã PUBLIC** — mọi commit/log/tài liệu từ nay ai cũng đọc được. Trước khi commit phải
  soát kỹ hơn: không đường dẫn máy cá nhân, không dữ liệu danh bạ, không token. Lịch sử git đã
  rà lại: chưa từng có file `.csv`/`.vcf`/`.db` nào được theo dõi.
- **tkinter không an toàn đa luồng** — cập nhật UI từ thread nền BẮT BUỘC đi qua `self._uiCall`
  (đẩy vào `queue.Queue`), không bao giờ gọi thẳng `root.after`/widget từ thread khác.
- **Ký số**: chứng thư tự ký ký được, có dấu thời gian, nhưng `Get-AuthenticodeSignature` trả
  `UnknownError` trên máy khác và **SmartScreen vẫn cảnh báo** — đây là giới hạn của phương án
  miễn phí, không phải lỗi script. Cách xác thực đang dùng là `SHA256SUMS.txt`.
  `-TrustLocally` mở hộp thoại xác nhận của Windows, không tự động hóa được.
- **Cách chạy GUI/test Windows từ WSL** (giữ nguyên từ phiếu 20260820-02): `rsync` mã nguồn sang
  `$(wslpath "$(powershell.exe -NoProfile -Command '$env:TEMP')")/<thư mục tạm>` rồi gọi
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "…"` với
  `%LOCALAPPDATA%\Programs\Python\Python311\python.exe`. Nhớ `chcp 65001` và
  `$env:PYTHONIOENCODING='utf-8'`, và **xóa thư mục tạm khi xong**.
- **File `.ps1` giữ UTF-8 CÓ BOM, xuống dòng LF** như `build-win.ps1` — đừng "dọn" BOM.
- Workflow chạy tay được từ tab Actions (`workflow_dispatch`): build + upload artifact, không tạo
  Release; chỉ khi đẩy tag `v*` mới đính file vào Release.

## 6. Kết quả xử lý (agent nhận điền sau khi thực hiện)

- (phiên sau điền)
