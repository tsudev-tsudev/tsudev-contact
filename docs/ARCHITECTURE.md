# ARCHITECTURE.md - Quyết định kiến trúc của repo tsudev-contact

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
| Đóng gói | PyInstaller - `Contacts.spec` | `console=False`, nhúng `icon.png` qua `datas` |

## 3. Bố cục mã nguồn

`contacts.pyw` ở gốc chỉ còn là **điểm khởi chạy mỏng** (nạp `sys.path` rồi gọi `src.main.app.main`)
- giữ nguyên để `Contacts.spec` và thói quen bấm đúp file không đổi.

```
src/
├── app_info.py                     # tên app, phiên bản, tác giả - khai báo 1 nơi
├── main/app.py                     # AppLauncher: splash → cửa sổ chính + hiệu ứng trượt
├── features/
│   ├── csv_to_vcf/converter.py     # logic chuyển đổi THUẦN, không import tkinter
│   ├── csv_to_vcf/ui.py            # ContactsApp: chọn file, ghép cột, nhật ký
│   ├── preview/ui.py               # PreviewWindow: treeview + phân trang
│   └── splash/{matrix,system_check}.py
├── services/
│   ├── database.py                 # DatabaseManager (SQLite)
│   ├── settings.py                 # tùy chọn người dùng (chủ đề) trong temp; thư mục dữ liệu app
│   └── tokens.py                   # đọc tokens/design-tokens.json → API màu/font/spacing
└── utils/{resource_path,dpi}.py
tests/test_csv_to_vcf.py            # test tích hợp luồng CSV → SQLite → vCard
```

**Quy tắc đặt tên**: thư mục/file theo `snake_case` thay vì `kebab-case` - Python không
import được tên có dấu gạch ngang. Áp dụng ngoại lệ "theo chuẩn ngôn ngữ" của
`docs/PROJECT_STRUCTURE.md`; ngữ nghĩa tên giữ nguyên. Hàm/biến dùng `camelCase` đúng quy ước.

**Ranh giới UI ↔ logic**: `converter.py` không biết gì về tkinter; nó báo tiến trình và lỗi
từng dòng qua callback `onProgress` / `onRowError`. `ui.py` chạy nó trong thread nền và
đẩy mọi cập nhật về main thread qua `_uiCall()` (bọc `root.after`). Nhờ vậy toàn bộ luồng
chuyển đổi test được mà không cần màn hình.

**Giao diện dùng token**: `src/services/tokens.py` đọc thẳng `tokens/design-tokens.json`
(đúng chỉ dẫn trong chính file token). Cỡ chữ truyền cho tkinter dưới dạng **số âm = pixel**
để khớp đơn vị px của token. Màn hình hiệu ứng dùng bảng màu chủ đề `dark`.

**Chủ đề sáng/ấm/tối**: menu *Giao diện* đổi chủ đề ngay lúc chạy và ghi nhớ vào
`settings.json` trong thư mục dữ liệu tạm. Chủ đề `light` dùng ttk theme `vista` (widget vẽ
theo native Windows, đẹp nhưng **bỏ qua màu nền**); `warm`/`dark` bắt buộc chuyển sang theme
`clam` vì cần đổi nền - `_configureNonNativeStyles()` tô lại Entry/Combobox/Button/Treeview/
Progressbar/Scrollbar từ tokens. Widget Tk cổ điển (nút chính, ô nhật ký) không theo
`ttk.Style` nên được tô riêng trong `_restyleClassicWidgets()`.

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
  lúc chạy, **không hard-code** - nên việc ignore không ảnh hưởng ứng dụng.
- **Chạy hoàn toàn cục bộ**: không gọi mạng, không secret, không biến môi trường
  (xem `.env.example`). Không phát sinh chi phí hạ tầng.
- **Chỉ 1 dependency ngoài stdlib** (`Pillow`) - giữ nguyên tắc "thư viện nhẹ" của AGENTS.md mục 4.

## 6. Lỗi đã sửa khi tái cấu trúc (20/08/2026)

Ba lỗi tồn tại trong bản 1 file, phát hiện khi tách module:

1. **`sqlite3.Row` không có `.get()`** - `contact.get('email')` trong luồng xuất VCF ném
   `AttributeError` ngay liên hệ đầu tiên, rơi vào `except` và báo "Lỗi nghiêm trọng"
   → **chức năng xuất VCF không bao giờ chạy xong**. `PreviewWindow` mắc đúng lỗi này.
   Đã đổi sang truy cập bằng khóa (`contact['email'] or ''`), có test chặn hồi quy.
2. **Sai số tham số** - `_update_progress(value, text)` được gọi với 3 tham số ở nhánh
   hoàn tất và nhánh lỗi → `TypeError`, thanh tiến trình không bao giờ chốt 100%.
3. **Rò rỉ kết nối SQLite** - `with sqlite3.connect(...)` chỉ commit/rollback, không đóng
   kết nối. Đã bọc `contextlib.closing`.

Ngoài ra, CSDL tạm chuyển từ thư mục cài đặt (`resourcePath`) sang thư mục temp của người
dùng: thư mục cài đặt có thể chỉ-đọc (Program Files), và file đó chứa PII.

### 6.1. Lỗi phát hiện khi chạy thử GUI thật trên Windows (20/08/2026)

4. **Nút "BẮT ĐẦU CHUYỂN ĐỔI" mất chữ** - style `Highlight.TButton` đặt
   `foreground=on-primary` (trắng) kèm `background=primary`, nhưng theme `vista` của ttk vẽ
   nút bằng native theme và **bỏ qua `-background`** → chữ trắng trên nền trắng khi nút có
   focus. Đã đổi sang `tk.Button` (widget cổ điển tôn trọng `bg`/`fg`), màu vẫn lấy từ tokens.
   *Bài học: trên Windows, style ttk chỉ nên chỉnh `foreground`/`font`; muốn đổi nền nút phải
   dùng `tk.Button` hoặc theme `clam`.*
5. **Đoán cột CSV bỏ sót trường bắt buộc SĐT** - hàm đoán cũ so khớp `field in header`, nên
   cột `Phone`/`Số điện thoại` không khớp trường `number`, `Note` không khớp `notes`; người
   dùng luôn phải chọn tay 2 trường bắt buộc. Đã thay bằng `converter.guessHeader` + bảng
   `FIELD_ALIASES` (Anh/Việt, bỏ dấu, khớp nguyên tên trước rồi mới khớp một phần -
   hỗ trợ cả `Phone 1 - Value` của Google Contacts). 5 test bao phủ.

### 6.2. Lỗi phát hiện khi tự động hóa kiểm thử GUI (20/08/2026)

6. **Gọi `root.after` từ thread nền** - `ContactsApp._uiCall` chạy trong thread chuyển đổi và
   gọi thẳng `self.root.after(...)`, tức là chạm vào interpreter Tcl từ thread khác. Khi có
   `mainloop()` thật thì thường "may mà chạy", nhưng test tự động (quay vòng lặp bằng
   `update()`) làm nó ném `RuntimeError: main thread is not in main loop` - đúng bản chất:
   tkinter **không an toàn đa luồng**. Đã đổi sang `queue.Queue`: thread nền chỉ `put()`,
   main thread có `_pumpUiQueue` (hẹn lại mỗi 30ms) rút hàng đợi và đụng widget. Lượt hẹn
   đang treo được `after_cancel` khi cửa sổ gốc bị hủy, tránh Tcl báo `invalid command name`.
   *Bài học: mọi cập nhật UI từ thread nền phải đi qua hàng đợi do main thread rút.*

## 7. Nợ kỹ thuật còn lại

1. Chưa có trình cài đặt thật (Inno/NSIS): bản phát hành là **1 file .exe onefile** mang tên
   `..._x64-setup.exe`. Thêm installer khi cần shortcut Start Menu / gỡ cài đặt.
2. Chưa ký số bằng chứng thư của CA - SmartScreen vẫn cảnh báo ở lần chạy đầu trên máy khác.
   `scripts/sign-win.ps1` đã có sẵn quy trình ký (Authenticode + dấu thời gian, dùng công cụ
   có sẵn trong Windows, không tốn phí), nhưng **chứng thư tự ký không gỡ được cảnh báo** -
   muốn hết cảnh báo phải mua chứng thư OV/EV, không có phương án miễn phí tương đương.
   Cách xác thực miễn phí đang dùng: `release/SHA256SUMS.txt` đính kèm mỗi Release.

## 8. Kiểm thử GUI

Đã tự động hóa: `tests/test_gui_smoke.py` chạy đúng kịch bản dưới đây bằng cách gọi thẳng
handler của widget và tự quay vòng lặp sự kiện (`update()`), không cần bấm chuột thật.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\test-gui-win.ps1          # toàn bộ test
powershell -ExecutionPolicy Bypass -File scripts\test-gui-win.ps1 -GuiOnly # chỉ phần GUI
```

Máy không có tkinter hoặc không có phiên đồ họa (WSL, SSH, Session 0) → cả lớp test **tự bỏ
qua**, không làm đỏ bộ test chung. Workflow phát hành chạy trên `windows-latest` nên các test
này chạy thật trong CI ở bước `Chạy test`.

Test dồn mọi dữ liệu app (`settings.json`, CSDL tạm) vào thư mục dùng một lần bằng cách đổi
`tempfile.tempdir`, và thay `messagebox` bằng bản ghi nhận để hộp thoại không chặn vòng lặp.

Kịch bản được phủ (giữ lại để đối chiếu khi cần chạy tay):

1. Chuỗi khởi động: màn hình kiểm tra hệ thống → mưa ký tự → cửa sổ chính hiện ra, tiêu đề
   chứa đúng chuỗi phiên bản.
2. Chọn CSV → 7 trường tự ghép đủ, hai trường bắt buộc không còn "(Bỏ qua)".
3. Chuyển đổi → nhật ký báo dòng thiếu Tên/SĐT (tô màu `danger`), hộp thoại thành công,
   file `.vcf` có đúng số liên hệ hợp lệ.
4. "Xem thử Danh bạ" → tiêu đề cột là **nhãn vCard**, dòng lỗi tô nền đỏ, phân trang đúng tổng số.
5. Menu *Giao diện* → Sáng / Ấm / Tối: nền cửa sổ và màu nút khớp tokens, nút chính không mất
   chữ, lựa chọn được ghi nhớ trong `settings.json`.

Việc chưa tự động được (vẫn phải nhìn bằng mắt khi đổi giao diện lớn): bố cục có bị vỡ không,
hiệu ứng trượt/mờ có mượt không, và bản `.exe` sau khi đóng gói có chạy trên máy sạch không.
