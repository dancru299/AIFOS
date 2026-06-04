# Hướng dẫn cấu hình Email Job-Alert (Upwork + LinkedIn → Gmail → AI-FOS)

> Mục tiêu: để **Gmail Inbox Hunter** của AI-FOS tự đọc email job-alert từ Upwork/LinkedIn trong hộp thư Gmail, bóc link job và đẩy vào pipeline (chấm điểm LLM → báo Telegram). Đây là cách lấy **job freelance thật** (khác với RSS toàn tin tuyển full-time).

Liên quan: [HUONG-DAN-VAN-HANH.md](HUONG-DAN-VAN-HANH.md) (vận hành tổng thể).

---

## 0. Cơ chế hoạt động (đọc để hiểu vì sao phải cấu hình đúng)

Mỗi vòng Scout (~15 phút), `GmailInboxScout` ([app/services/scouts/gmail_fetcher.py](app/services/scouts/gmail_fetcher.py)) làm:

1. **Đăng nhập IMAP** vào Gmail bằng `AIFOS_GMAIL_EMAIL` + `AIFOS_GMAIL_APP_PASSWORD` (App Password, không phải mật khẩu thường).
2. **Mở mailbox** `AIFOS_GMAIL_MAILBOX` (mặc định `INBOX`).
3. **Tìm email** trong `AIFOS_GMAIL_SEARCH_WINDOW_DAYS` ngày gần nhất (mặc định 2) có **subject chứa** một trong các chuỗi ở `AIFOS_GMAIL_ALERT_SUBJECTS`.
4. **Bóc link job** trong email: chỉ nhận link tới `linkedin.com/jobs/view/<id>` hoặc `upwork.com/...­/jobs/...`. Link khác bị bỏ.
5. Sinh job (title + mô tả + ngân sách + địa điểm đoán được) → đẩy `POST /api/v1/jobs/ingest` → Analyst chấm điểm → ≥ ngưỡng thì báo Telegram.

### 3 quy tắc sống còn

| Quy tắc | Hệ quả nếu sai |
|---|---|
| **Subject phải khớp** (chứa-chuỗi, không phân biệt hoa thường) | Subject mặc định `Upwork Job Alert`/`LinkedIn Job Alert` thường **không khớp** email thật → 0 job. **Phải chỉnh** theo subject thật (mục 5). |
| **Email phải nằm trong mailbox đang quét** | Nếu bộ lọc Gmail "Skip Inbox" (archive) email alert mà bạn vẫn để `AIFOS_GMAIL_MAILBOX=INBOX` → không tìm thấy. |
| **Email phải chứa link job trực tiếp** | LinkedIn/Upwork alert đều có link `…/jobs/view/…` / `…/jobs/…` nên thường OK; nhưng vài bản tóm tắt chỉ có nút "Xem tất cả" → bóc được ít. |

> ✅ **Tin tốt:** bộ lọc link rất chặt (chỉ Upwork/LinkedIn job URL), nên subject filter **rộng tay một chút cũng an toàn** — email lọt qua subject nhưng không có link job sẽ tự cho ra 0 job. Vì vậy nên đặt subject filter **bao quát** thay vì quá hẹp.

---

## 1. Các biến `.env` liên quan

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `AIFOS_GMAIL_EMAIL` | — | Địa chỉ Gmail nhận alert |
| `AIFOS_GMAIL_APP_PASSWORD` | — | **App Password 16 ký tự** (mục 2) |
| `AIFOS_GMAIL_ALERT_SUBJECTS` | `Upwork Job Alert,LinkedIn Job Alert` | Danh sách chuỗi subject (phân tách bằng dấu phẩy). **Cần chỉnh** (mục 5) |
| `AIFOS_GMAIL_MAILBOX` | `INBOX` | Mailbox/nhãn IMAP để quét |
| `AIFOS_GMAIL_SEARCH_WINDOW_DAYS` | `2` | Chỉ quét email trong N ngày gần nhất |
| `AIFOS_GMAIL_IMAP_HOST` / `_PORT` | `imap.gmail.com` / `993` | Server IMAP |
| `AIFOS_GMAIL_MARK_SEEN` | `false` | `false` = đọc ở chế độ chỉ-đọc, không đánh dấu đã đọc |

> Bạn đã cấu hình sẵn `AIFOS_GMAIL_EMAIL` + `AIFOS_GMAIL_APP_PASSWORD` (preflight báo "Gmail" đã bật). Mục 2 chỉ để tham khảo nếu cần làm lại. **Việc còn thiếu chủ yếu là mục 3–5.**

Có thể chỉnh tất cả qua **`/admin`** (mục Scout Sources) hoặc sửa trực tiếp `.env`.

---

## 2. (Nếu cần) Bật IMAP + tạo App Password Gmail

1. Bật **2-Step Verification**: https://myaccount.google.com/security → "2-Step Verification".
2. Tạo App Password: https://myaccount.google.com/apppasswords → đặt tên (vd `AI-FOS`) → Google sinh chuỗi **16 ký tự** (dạng `abcd efgh ijkl mnop`).
3. Dán vào `.env` (bỏ khoảng trắng hoặc giữ đều được):
   ```
   AIFOS_GMAIL_EMAIL=ban@gmail.com
   AIFOS_GMAIL_APP_PASSWORD=abcdefghijklmnop
   ```
4. Bật IMAP trong Gmail: Gmail → ⚙️ See all settings → **Forwarding and POP/IMAP** → **Enable IMAP** → Save.

---

## 3. Bật Job-Alert trên **Upwork** → gửi về Gmail

> Điều kiện: **email tài khoản Upwork = Gmail đã cấu hình** (hoặc thiết lập chuyển tiếp ở mục 6).

1. Đăng nhập Upwork → **Find Work**.
2. Gõ từ khoá + đặt bộ lọc (ví dụ: `python automation`, Fixed-price, Entry/Intermediate, Client US…).
3. Bấm **Save search** (lưu tìm kiếm). Đặt tên dễ nhớ (vd `py-automation`).
4. Vào **Settings → Notifications** (https://www.upwork.com/nx/settings/notifications): bật **Email** cho **Saved searches / New job postings**. Chọn tần suất **Instant** hoặc **Daily** (Instant = nhiều email, bắt job nhanh hơn).
5. Đảm bảo email tài khoản đúng là Gmail: **Settings → Contact info** → Email.

**Mẹo nhiều job:** tạo **3–6 saved search** với từ khoá khác nhau (vd `web scraping`, `fastapi`, `landing page`, `fix bug python`, `telegram bot`, `data entry automation`). Mỗi cái là một luồng job riêng.

---

## 4. Bật Job-Alert trên **LinkedIn** → gửi về Gmail

> Điều kiện: **email tài khoản LinkedIn = Gmail đã cấu hình** (hoặc chuyển tiếp ở mục 6). Alert LinkedIn gửi từ `jobalerts-noreply@linkedin.com`.

1. Đăng nhập LinkedIn → **Jobs**.
2. Gõ từ khoá + chọn **Remote**, mức kinh nghiệm, địa điểm…
3. Bật công tắc **Set alert** (Tạo thông báo) ở đầu trang kết quả.
4. Quản lý tại **Jobs → Job alerts** (https://www.linkedin.com/jobs/job-alerts/): với mỗi alert chọn **Email** + tần suất (**Daily** khuyên dùng; Weekly thì thưa).
5. Kiểm tra email nhận thông báo: **Settings & Privacy → Sign in & security → Email addresses** (đặt Gmail làm email chính), và **Communications → Email** bật Job alerts.

**Mẹo nhiều job:** tạo nhiều alert theo từng từ khoá/role (vd `Python Developer Remote`, `Automation Engineer`, `Web Scraping`, `Backend Freelance`).

---

## 5. ⭐ Chỉnh `AIFOS_GMAIL_ALERT_SUBJECTS` cho khớp subject thật (QUAN TRỌNG NHẤT)

Subject mặc định **gần như chắc chắn không khớp** email thật. Cách làm chuẩn:

1. **Chờ 1–2 alert đầu tiên về Gmail.** Mở email, **copy nguyên subject**. Ví dụ thường gặp (chỉ là tham khảo, hãy lấy subject THẬT của bạn):
   - LinkedIn: `"15 new jobs for Python Developer"`, `"Your job alert for backend developer"`, `"…and more new jobs"`.
   - Upwork: `"New jobs: py-automation"`, `"Upwork job digest"`, `"X new jobs match your search"`.
2. **Chọn một chuỗi con ổn định** lặp lại ở mọi alert (không phụ thuộc số lượng/từ khoá). Ví dụ từ subject trên:
   - LinkedIn → `new jobs` hoặc `job alert`.
   - Upwork → `new jobs` hoặc tên saved search của bạn, hoặc `Upwork`.
3. **Điền vào `.env`** (phân tách bằng dấu phẩy, không phân biệt hoa thường, khớp kiểu *chứa*):
   ```
   AIFOS_GMAIL_ALERT_SUBJECTS=new jobs,job alert,jobs for,Upwork
   ```
   > Vì bộ lọc link rất chặt, để rộng tay vẫn an toàn. Nếu vẫn không ra job, nới rộng thêm; nếu kéo về quá nhiều email rác (vẫn ra 0 job nên vô hại, chỉ tốn IMAP), thu hẹp lại.
4. **Lưu** rồi khởi động lại (`Ctrl+C` rồi `python scripts/start.py`) hoặc Save trong `/admin`.

> ⚠️ Nếu để **trống** `AIFOS_GMAIL_ALERT_SUBJECTS`, hiện code sẽ **không** quét (không có fallback "lấy tất cả"). Luôn để ít nhất 1 chuỗi.

---

## 6. (Nếu email tài khoản KHÁC Gmail đã cấu hình) — Chuyển tiếp

Nếu tài khoản Upwork/LinkedIn dùng email khác, chọn 1:

- **Đổi email tài khoản** Upwork/LinkedIn sang Gmail đã cấu hình (đơn giản nhất).
- **Tự động chuyển tiếp** từ hộp thư kia sang Gmail: ở hộp thư nguồn tạo filter `from:upwork.com` / `from:linkedin.com` → Forward to `ban@gmail.com`. *Lưu ý:* khi chuyển tiếp, subject thường giữ nguyên hoặc thêm tiền tố `Fwd:` — nhớ kiểm tra lại subject (mục 5).

---

## 7. (Khuyên dùng) Gmail filter để gọn gàng + chắc chắn

Để alert không lẫn và luôn nằm trong mailbox đang quét:

1. Gmail → ⚙️ → **Filters and Blocked Addresses → Create a new filter**.
2. Ô **From**: `upwork.com OR linkedin.com` (hoặc tạo 2 filter riêng: `notifications@upwork.com`, `jobalerts-noreply@linkedin.com`).
3. **Create filter** → tick **Apply the label** → tạo nhãn `AIFOS-Jobs`. **KHÔNG** tick "Skip the Inbox" nếu vẫn để `AIFOS_GMAIL_MAILBOX=INBOX`.
4. (Nâng cao) Nếu muốn email alert KHÔNG ở Inbox cho gọn: tick "Skip the Inbox" + đặt `AIFOS_GMAIL_MAILBOX=AIFOS-Jobs` để Hunter quét đúng nhãn đó. Vẫn phải giữ `AIFOS_GMAIL_ALERT_SUBJECTS` khớp subject.

---

## 8. Kiểm tra (bắt buộc trước khi tin dùng)

Chạy thử Scout ở chế độ **xem trước** (không đẩy job):

```powershell
python scripts/run_scouts.py --dry-run
```

- Tìm dòng có `[upwork]` hoặc `[linkedin]` → ✅ Hunter đọc được email và bóc link.
- Chỉ thấy `[weworkremotely]`/`[remoteok]` → email chưa khớp. Quay lại **mục 5** (subject), kiểm tra email có nằm trong mailbox (mục 7) và đúng cửa sổ ngày (`AIFOS_GMAIL_SEARCH_WINDOW_DAYS`).

Chạy thật 1 vòng (đẩy vào pipeline):

```powershell
python scripts/run_scouts.py --once
```

---

## 9. Tinh chỉnh

| Muốn | Đổi biến |
|---|---|
| Bắt được email cũ hơn | Tăng `AIFOS_GMAIL_SEARCH_WINDOW_DAYS` (vd 5–7) |
| Nhiều job mỗi vòng hơn | Tăng `AIFOS_SCOUT_LIMIT_PER_SOURCE` |
| Quét đúng nhãn riêng | `AIFOS_GMAIL_MAILBOX=AIFOS-Jobs` |
| Đánh dấu đã đọc sau khi xử lý | `AIFOS_GMAIL_MARK_SEEN=true` (mặc định false = không đụng trạng thái đọc) |

> Job trùng (cùng URL) sẽ **không báo lại** nhờ pipeline tự khử trùng — yên tâm để Instant/Daily.

---

## 10. Khắc phục sự cố

| Triệu chứng | Nguyên nhân & cách xử |
|---|---|
| `--dry-run` không có `[upwork]`/`[linkedin]` | Subject chưa khớp (mục 5) · email đã bị archive khỏi INBOX (mục 7) · ngoài cửa sổ ngày · email tài khoản khác Gmail (mục 6) |
| Login IMAP lỗi | Sai **App Password** (không dùng mật khẩu thường) · chưa bật 2FA/IMAP (mục 2) |
| Có email nhưng 0 job | Email không chứa link `…/jobs/view/…` (LinkedIn) hay `…/jobs/…` (Upwork) — vài bản digest chỉ có nút tổng; tạo alert chi tiết hơn hoặc tăng tần suất |
| Job bóc ra title/mô tả nghèo | Bản chất email tóm tắt ngắn; Analyst vẫn chấm được, nhưng điểm có thể thấp |
| Ra quá nhiều email rác bị quét | Thu hẹp `AIFOS_GMAIL_ALERT_SUBJECTS` (nhưng email rác không có link job → vẫn 0 job, chỉ chậm hơn chút) |

---

## 11. Tóm tắt checklist

- [ ] Gmail: 2FA + **App Password** + IMAP bật; `.env` có `AIFOS_GMAIL_EMAIL` + `AIFOS_GMAIL_APP_PASSWORD`.
- [ ] Upwork: ≥1 saved search + bật email notification về Gmail (mục 3).
- [ ] LinkedIn: ≥1 job alert + email về Gmail (mục 4).
- [ ] Đã xem subject email thật và set **`AIFOS_GMAIL_ALERT_SUBJECTS`** cho khớp (mục 5).
- [ ] (Tuỳ chọn) Gmail filter gắn nhãn `AIFOS-Jobs`, giữ ở mailbox đang quét (mục 7).
- [ ] `python scripts/run_scouts.py --dry-run` thấy dòng `[upwork]`/`[linkedin]`.
- [ ] Khởi động lại hệ thống: `python scripts/start.py`.
