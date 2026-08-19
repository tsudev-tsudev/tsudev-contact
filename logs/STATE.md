# STATE.md — Trạng thái project (agent đọc đầu phiên, cập nhật cuối phiên)

## Hàng đợi task (làm từ trên xuống)
- [ ] T1 — Bảo mật: đưa dữ liệu cá nhân (`danh_ba_102_xa.csv`) vào `.gitignore`; `git init` + commit đầu sạch
- [ ] T2 — Bổ sung file thiếu theo PROJECT_STRUCTURE.md: `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `.env.example`
- [ ] T3 — Tái cấu trúc `contacts.pyw` (28KB, 1 file gốc) sang `src/` (main/features/services/utils) — việc lớn, chia nhiều phiên
- [ ] T4 — Chuẩn hóa UI: thay màu/cỡ chữ hard-code trong code bằng giá trị truy ngược về `tokens/design-tokens.json`
- [ ] T5 — Tạo repo GitHub `tsudev-contact` cho tài khoản https://github.com/tsudev-tsudev + push
      CHẶN: `gh` đang đăng nhập `dieuhanhcongviecxanuicam`, cần chủ project đăng nhập `tsudev-tsudev`

## Đang thực hiện
| Task | Agent | Bắt đầu |
|---|---|---|
| T1 — Bảo mật + git init | agent-session-20260820 | 00:43 20/08/2026 |

## Đã hoàn thành (mới nhất trên cùng)
- 20/08/2026 — Dọn thư mục rỗng rác `{docs/templates,tokens,logs/handover}` (brace-expansion hỏng lúc khởi tạo repo)
- 19/08/2026 — Khởi tạo bộ quy ước v1.0.0

## Quyết định quan trọng
- 19/08/2026 — Dùng Inter làm font chuẩn; token là nguồn chân lý duy nhất; region ưu tiên Singapore → Nhật Bản.
