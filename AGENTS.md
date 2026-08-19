# AGENTS.md — QUY ƯỚC BẮT BUỘC CHO MỌI LẬP TRÌNH VIÊN & AGENT AI

> **ĐỌC FILE NÀY ĐẦU TIÊN trong mọi phiên làm việc mới.** Áp dụng cho toàn bộ project.
> Các file quy ước (`AGENTS.md`, `docs/*`, `tokens/*`, `.gitignore`) là **BẤT KHẢ XÂM PHẠM**: chỉ đọc-hiểu-tuân thủ, KHÔNG được sửa/xóa trừ khi chủ project yêu cầu trực tiếp.

## 0. Câu lệnh khởi động phiên (dán vào đầu mỗi phiên terminal mới)

```
Đọc AGENTS.md, logs/STATE.md và phiếu bàn giao mới nhất trong logs/handover/.
Tuân thủ toàn bộ quy ước. Nhận task tiếp theo trong hàng đợi của STATE.md,
khóa file mình sẽ sửa vào logs/LOCKS.md rồi mới bắt đầu. Trả lời ngắn gọn,
tiết kiệm token, không lặp lại nội dung đã có trong file quy ước.
```

## 1. Nguyên tắc tiết kiệm token / context

- Không đọc lại file đã nắm nội dung trong cùng phiên; không in toàn bộ file dài ra hội thoại — chỉ trích phần liên quan.
- Trả lời và ghi log **ngắn gọn, gạch đầu dòng, không văn mẫu**. Không lặp lại quy ước đã có sẵn trong docs.
- Mọi tri thức dùng lại được (quyết định kiến trúc, cách chạy build, lỗi đã gặp) ghi vào file markdown tương ứng **một lần duy nhất**, các phiên sau chỉ tham chiếu đường dẫn.
- Task lớn phải chia nhỏ; làm xong phần nào chốt phần đó vào log ngay để mất phiên không mất công.

## 2. Đội ngũ agent & chống giẫm chân (File Lock + Phiếu bàn giao)

- Mỗi agent nhận **một nhiệm vụ duy nhất** tại một thời điểm, ghi rõ trong `logs/STATE.md` (mục "Đang thực hiện").
- **Trước khi sửa bất kỳ file nào**: kiểm tra `logs/LOCKS.md`. File chưa ai khóa → thêm dòng khóa `<đường dẫn> | <tên agent/nhiệm vụ> | <HH:mm DD/MM/YYYY>` rồi mới sửa. Sửa xong → xóa dòng khóa.
- File **đang bị agent khác khóa** → TUYỆT ĐỐI không sửa. Thay vào đó tạo phiếu bàn giao tại `logs/handover/` theo mẫu `docs/templates/HANDOVER.md`, ghi rõ cần thay đổi gì, vì sao, tiêu chí hoàn thành.
- Agent đang giữ khóa **có trách nhiệm đọc phiếu gửi đến mình trước khi nhả khóa** và thực hiện/ghi kết quả vào chính phiếu đó.
- Không bao giờ tự ý can thiệp nhiệm vụ, nhánh git, hoặc file của agent khác đang thực hiện.

## 3. Git, bảo mật & .gitignore

- `.gitignore` gốc của repo là chuẩn tối thiểu. Trong quá trình làm việc, hễ **tạo ra** file/thư mục chứa secret, credential, cache, build output, dữ liệu cá nhân → **bổ sung ngay vào `.gitignore` trước khi commit**.
- **Checklist bắt buộc trước mọi commit / PR / merge / deploy / push:**
  1. `git status` — không có file lạ ngoài phạm vi task.
  2. Không có secret/API key/token/mật khẩu/connection string trong diff (kể cả trong comment, log, file test). Secret chỉ nằm trong `.env*` (đã ignore) hoặc secret manager của nền tảng.
  3. File mới thuộc nhóm nhạy cảm/cache đã vào `.gitignore`.
  4. Build/test pass ở mức tối thiểu của task.
  5. Commit message: `loại(phạm-vi): mô tả ngắn` — ví dụ `fix(auth): sửa hết hạn token`.
- Lỡ commit secret → coi secret đã lộ: thu hồi/đổi khóa ngay, xóa khỏi lịch sử, ghi sự cố vào `logs/STATE.md`.
- Không tắt HTTPS/SSL verify, không hạ cấp thuật toán mã hóa, không mở cổng/quyền rộng hơn mức task cần.

## 4. Tiết kiệm chi phí hạ tầng (mặc định cho mọi project)

- **Luôn ưu tiên gói miễn phí** trước khi cân nhắc trả phí: GitHub (repo/Actions/Pages), Cloudflare (Pages/Workers/R2/DNS), Vercel/Netlify free tier, Supabase/Neon free tier, Oracle Cloud Always Free… Chỉ đề xuất trả phí khi free tier chứng minh không đủ, kèm số liệu.
- Chọn **region gần Việt Nam**: ưu tiên **Singapore**, kế đến **Nhật Bản (Tokyo/Osaka)** cho mọi dịch vụ có chọn vùng (server, DB, CDN origin, storage).
- Tận dụng cache/CDN miễn phí, nén tài nguyên, tránh polling — giảm băng thông là giảm chi phí.
- Trước khi thêm dependency/dịch vụ mới: kiểm tra đã có thứ tương đương trong project chưa; ưu tiên thư viện nhẹ, mã nguồn mở.

## 5. Kết thúc phiên & bàn giao (bắt buộc)

Khi (a) hàng đợi việc trong `logs/STATE.md` đã cạn, (b) được yêu cầu bàn giao, hoặc (c) context sắp cạn:
1. Ghi vào `logs/STATE.md`: việc đã làm, việc dang dở + bước tiếp theo cụ thể, quyết định quan trọng.
2. Tạo phiếu bàn giao `logs/handover/YYYYMMDD-NN_<chủ-đề>.md` theo mẫu (đủ để phiên sau làm tiếp **không cần hỏi lại**, kể cả khi máy tắt đột ngột).
3. Nhả toàn bộ khóa của mình trong `logs/LOCKS.md`.
4. Dọn tàn dư: xóa file tạm/scratch, không để thay đổi chưa commit ngoài phạm vi bàn giao — chuẩn hóa cây làm việc sạch để phiên sau không tốn "chi phí chết".
5. Đề xuất chủ project **đóng terminal, mở phiên mới** cho task kế tiếp.

## 6. Quy ước giao diện & phát hành

- Mọi thay đổi UI phải dùng token trong `tokens/` — cấm hard-code màu/cỡ chữ/radius. Chi tiết: `docs/DESIGN_SYSTEM.md`.
- Ngày tháng hiển thị dạng số `DD/MM/YYYY` (ví dụ `01/02/2027`).
- Tên bản phát hành app/tool theo mục 6 của `docs/DESIGN_SYSTEM.md` (ví dụ `tsudev-swico_26.8.1901_x64-setup.exe`).
- Cấu trúc thư mục chuẩn: `docs/PROJECT_STRUCTURE.md` — tạo file mới phải đặt đúng vị trí quy định.
