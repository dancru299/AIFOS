# AI Freelancer Operating System — Hướng dẫn vận hành thật

> Tài liệu này tóm tắt toàn bộ dự án, cách setup, **những key cần điền**, và cách vận hành để hệ thống chạy thật từ đầu đến cuối. Đọc một lượt rồi làm theo phần “Checklist đi vào hoạt động”.

---

## 1. Hệ thống này làm gì?

Một “nhân viên freelancer AI” chạy headless: tự **săn job → chấm điểm → xin bạn duyệt qua Telegram → viết proposal → làm việc thật (code/viết/scrape) → tự QA → giao kết quả**. Bạn điều khiển toàn bộ bằng các nút bấm trong Telegram.

**Luồng tổng quát:**

```
Scout (săn job)            Analyst (LLM chấm ROI)        Bạn duyệt qua Telegram
RSS / Reddit / Gmail / ─▶  điểm >= ngưỡng?         ─▶   👍 Approve & Pitch
Threads                    nếu đạt → báo Telegram         👎 Dismiss
        │                                                      │
        ▼                                                      ▼
   POST /api/v1/jobs/ingest                            Proposal (LLM soạn)
                                                              │ 🚀 Start Work
                                                              ▼
                                   ┌────────── Worker engine ──────────┐
                                   │ scaffold: LLM draft 1 lần + ZIP   │
                                   │ claude_code: agent tự lập kế hoạch│
                                   │   → code → test → tự QA → giao    │
                                   └───────────────────────────────────┘
                                                              │
                                                              ▼
                                          QA pass → DELIVERY_READY (báo Telegram)
                                          QA fail/blocker → ⚠️ ping bạn + nút 🔁 Làm lại
```

**Thành phần chính (mã nguồn):**

| Thành phần | Vị trí | Vai trò |
|---|---|---|
| API (FastAPI) | `app/main.py` | Nhận job, phục vụ Telegram webhook, Admin UI |
| Scout Agent | `app/services/scouts/` | Săn job từ RSS, Reddit, Gmail, Threads |
| Analyst | `app/services/analyst.py` | Chấm ROI bằng LLM |
| Proposal | `app/services/proposal.py` | Soạn proposal bằng LLM |
| Worker engines | `app/services/workers/` (scaffold), `app/services/agent/` (claude_code) | Làm sản phẩm |
| QA | `app/services/qa/`, agent review | Kiểm tra chất lượng |
| Telegram | `app/services/telegram*.py` | Thông báo + nút bấm điều khiển |
| Pipeline/State | `app/services/pipeline.py`, `app/state_machine.py` | Điều phối + máy trạng thái |

---

## 2. Yêu cầu

- **Python 3.11+**
- (Tùy chọn) **Claude Code CLI** đã đăng nhập — chỉ cần nếu dùng engine `claude_code`.
- (Production) Docker, hoặc Redis + Postgres.

---

## 3. Cài đặt nhanh (local, zero-infra)

```powershell
# 1. Tạo môi trường ảo + cài deps
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]

# 2. Tạo file .env từ mẫu
copy .env.example .env

# 3. Sửa hồ sơ năng lực của bạn (dùng để viết proposal)
#    portfolio/operator_portfolio.md  và  data/my_profile.md

# 4. Chạy API — LƯU Ý cổng 8001 (xem mục cảnh báo cổng bên dưới)
uvicorn app.main:app --reload --port 8001
```

Mở **http://127.0.0.1:8001/admin** để chỉnh cấu hình/nhập key bằng giao diện.
Mở **http://127.0.0.1:8001/docs** để xem/thử API.

> ⚠️ **Cổng phải khớp.** Scout gửi job vào `AIFOS_SCOUT_API_BASE_URL` (mặc định `http://127.0.0.1:8001`). Vì vậy hãy chạy API ở **cổng 8001**. Nếu muốn chạy cổng khác, đổi `AIFOS_SCOUT_API_BASE_URL` cho khớp.

### ⚡ Cách nhanh nhất — 1 lệnh chạy tất cả

Thay vì mở nhiều terminal, dùng launcher tích hợp:

```powershell
python scripts/start.py
```

Một lệnh tự động: kiểm tra `.env` (LLM, Telegram token + **chat_id**, nguồn săn job, worker engine…) → bật server đúng cổng → đợi `/healthz` khoẻ → chạy deep health-check → ping thử Telegram (xác nhận `chat_id`) → **bật luôn Scout đi săn job**. Nhấn **Ctrl+C** để dừng tất cả.

| Cờ | Tác dụng |
|---|---|
| `--no-scouts` | Chỉ chạy server, không săn job |
| `--no-ping` | Bỏ tin nhắn test Telegram khi khởi động |
| `--reload` | uvicorn tự khởi động lại khi sửa code |
| `--port N` / `--timeout N` | Đổi cổng / thời gian chờ server khoẻ |

> Lần chạy đầu, Scout nạp loạt job tồn → job đạt ngưỡng (`AIFOS_ANALYST_THRESHOLD`, mặc định 7.0) sẽ ping Telegram, nên có thể nhận vài tin cùng lúc + tốn ít quota LLM. Máy phải bật liên tục mới nhận job & bấm được nút Telegram.

---

## 4. BẢNG KEY CẦN ĐIỀN (quan trọng nhất)

Điền trong `.env` hoặc qua `/admin`. Tối thiểu để “chạy thật” là nhóm **Bắt buộc**.

### 4.1. Bắt buộc để có giá trị thật

| Biến | Lấy ở đâu | Dùng làm gì |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio → API Keys | Chấm ROI + soạn proposal (rẻ, đủ cho MVP) |
| `AIFOS_TELEGRAM_BOT_TOKEN` | Telegram `@BotFather` | Bot gửi thông báo + nhận nút bấm |
| `AIFOS_TELEGRAM_DEFAULT_CHAT_ID` | Nhắn cho bot 1 câu, rồi chạy `python scripts/get_telegram_chat_id.py` | Chat nhận thông báo |

> Không có key nào → hệ thống vẫn chạy ở **chế độ mock** (LLM giả) nếu `AIFOS_ALLOW_MOCK_LLM=true`, hữu ích để thử luồng nhưng **không tạo ra kết quả thật**.

### 4.2. Tùy theo cách nhận nút bấm Telegram

| Biến | Khi nào cần |
|---|---|
| `AIFOS_TELEGRAM_MODE` | `webhook` (cần URL HTTPS công khai) **hoặc** `polling` (chạy sau NAT/laptop, không cần URL) |
| `AIFOS_TELEGRAM_WEBHOOK_SECRET` | Chỉ khi dùng `webhook`. Tự đặt 1 chuỗi ngẫu nhiên; truyền đúng chuỗi đó khi đăng ký webhook |

### 4.3. Bật các nguồn săn job (Scout)

| Nguồn | Biến cần điền | Ghi chú |
|---|---|---|
| **RSS** (mặc định bật) | `AIFOS_RSS_FEED_URLS` | WeWorkRemotely + RemoteOK có sẵn. **Mẹo:** dùng RSSHub/rss.app biến **Facebook Page / profile Threads** thành RSS rồi dán vào đây → ingest dưới `source=rss`, không cần code |
| **Reddit** (mặc định bật) | `AIFOS_REDDIT_SUBREDDITS` | vd `forhire,freelance_forhire` |
| **Gmail Inbox Hunter** | `AIFOS_GMAIL_EMAIL`, `AIFOS_GMAIL_APP_PASSWORD` | App Password của Gmail (không phải mật khẩu thường). Đọc email job-alert Upwork/LinkedIn |
| **Threads** | `AIFOS_THREADS_API_TOKEN`, `AIFOS_THREADS_TARGET_USERNAMES` | Xem mục 7. Cần **App Review (Advanced Access)** để đọc tài khoản không phải của Meta |

### 4.4. Tùy chọn / nâng cao

| Biến | Mục đích |
|---|---|
| `AIFOS_OPENAI_API_KEY`, `AIFOS_ANTHROPIC_API_KEY` | LLM dự phòng (auto fallback khi Gemini lỗi) |
| `AIFOS_ADMIN_PASSWORD` | Bật khi mở `/admin` ra ngoài localhost (không đặt = chỉ cho localhost) |
| `AIFOS_WORKER_ENGINE` | `scaffold` (mặc định) hoặc `claude_code` (agent thật) |
| `AIFOS_AGENT_*` | Tinh chỉnh engine claude_code (xem mục 6) |
| `AIFOS_TASK_BACKEND` | `background` (mặc định, zero-infra) hoặc `arq` (Redis, bền) |

---

## 5. Vận hành nhận job qua Telegram

Có 2 cách bot nhận nút bấm. Chọn 1.

### Cách A — Polling (khuyên dùng cho laptop/PC nhà, không cần URL công khai)

```powershell
# .env
AIFOS_TELEGRAM_MODE=polling
```

Chạy API như bình thường — poller chạy **bên trong** tiến trình API, tự xoá webhook cũ. Approve / Dismiss / Start Work đều hoạt động. Giữ máy bật là nhận được job.

### Cách B — Webhook (cần URL HTTPS công khai, hợp cho server)

```powershell
# .env: AIFOS_TELEGRAM_MODE=webhook  + đặt AIFOS_TELEGRAM_WEBHOOK_SECRET
uvicorn app.main:app --port 8001
# Lộ ra ngoài bằng ngrok rồi đăng ký:
python scripts/set_telegram_webhook.py https://<ten-mien-cong-khai>/api/v1/telegram/webhook
# Hoặc tự động bằng ngrok:
python scripts/setup_ngrok_webhook.py 8001
```

---

## 6. Hai engine làm việc (Worker)

`AIFOS_WORKER_ENGINE` quyết định cách làm sản phẩm:

### `scaffold` (mặc định) — nhẹ, không cần CLI
LLM viết 1 lượt draft + đóng gói ZIP, tự QA vài vòng sửa. Phù hợp khi chưa cài Claude Code CLI.

### `claude_code` — agent thật (khuyên dùng để “làm như freelancer”)
Cần **Claude Code CLI đã đăng nhập** (`AIFOS_CLAUDE_BIN=claude`). Mỗi job có 1 folder riêng trong `AIFOS_DELIVERY_ROOT`. Luồng:

1. **PLANNING** — agent đọc brief, viết `PLAN.md`.
2. Nếu `AIFOS_AGENT_PLAN_GATE=true` → bạn duyệt kế hoạch qua Telegram (✅ Duyệt / ✋ Huỷ). Đặt `false` để agent tự chạy tiếp, chỉ ping khi xong/vướng.
3. **EXECUTE** — agent code thật, chạy test, sửa lỗi, viết `SUMMARY.md` (và `QUESTIONS.md` nếu vướng).
4. **REVIEW** — chấm % hoàn thành; ≥90% & pass → `DELIVERY_READY`; chưa đạt → tự sửa tối đa `AIFOS_AGENT_MAX_REPAIRS` lần.
5. Telegram báo kết quả kèm nút **✅ Nghiệm thu / 🔁 Làm lại** (khi xong) hoặc **🔁 Làm lại** (khi vướng). Câu hỏi trong `QUESTIONS.md` được trích thẳng vào tin nhắn.

**An toàn engine claude_code (đọc kỹ):**
- File chỉ nằm trong folder job (`cwd` + `--add-dir`).
- `AIFOS_AGENT_PERMISSION_MODE=bypassPermissions` (mặc định, cần cho Windows headless): ⚠️ ở chế độ này guardrail **không tự enforce** — agent chạy được mọi lệnh shell. Giảm rủi ro: trỏ `AIFOS_DELIVERY_ROOT` vào thư mục/ổ riêng (lý tưởng container/VM), giữ plan-gate bật.
- Muốn ép chặn lệnh nguy hiểm ngay cả khi bypass: đặt `AIFOS_AGENT_ENFORCE_GUARDRAIL_HOOK=true` (mặc định tắt) — cài PreToolUse hook chặn `rm -rf/sudo/git push/ssh...`.
- Mỗi job tốn usage Claude Code thật (log lại turns + USD mỗi run). **Luôn review trước khi gửi khách.**

---

## 7. Threads Scout (nguồn mới)

Threads **không có** API tìm kiếm toàn mạng. Scout này quét **whitelist** các profile mục tiêu qua endpoint chính thức **Profile Discovery**, lọc keyword tuyển dụng.

```powershell
# .env
AIFOS_THREADS_API_TOKEN=<access-token>
AIFOS_THREADS_TARGET_USERNAMES=@founder1,@indiehacker2,@agencyhub
# tùy chọn: AIFOS_THREADS_KEYWORDS, AIFOS_THREADS_USER_ID (mặc định "me")
```

**Ràng buộc thật (phải biết trước khi tin dùng):**
- Đọc profile **không phải của Meta** cần **Advanced Access qua App Review**. Standard Access chỉ trả tài khoản của Meta → vô dụng cho săn job đến khi được duyệt.
- Target cần **≥100 follower**; giới hạn **1.000 request/24h**. 1 request = 1 profile → giữ `số_target × số_chu_kỳ/ngày ≤ 1.000` (vd ~20 target ở mức 30’/lần).
- **Làn nhanh không cần App Review:** biến profile Threads công khai thành RSS (RSSHub/rss.app) → dán vào `AIFOS_RSS_FEED_URLS`. Chạy ngay, ingest dưới `source=rss`.

Bật xong, scout tự kích hoạt khi có cả token + usernames.

---

## 8. Chạy Scout (săn job)

Scout là tiến trình riêng, gửi job vào API qua HTTP.

```powershell
# Xem trước (không ingest)
python scripts/run_scouts.py --dry-run

# Chạy 1 vòng và đẩy job vào API
python scripts/run_scouts.py --once

# Chạy liên tục (mặc định mỗi 15 phút)
python scripts/run_scouts.py
```

> Nhớ API đang chạy ở đúng cổng `AIFOS_SCOUT_API_BASE_URL`.

---

## 9. VẬN HÀNH THẬT — happy path từ đầu đến cuối

1. Điền nhóm key **Bắt buộc** (mục 4.1) + chọn chế độ Telegram (mục 5).
2. Cập nhật `portfolio/operator_portfolio.md` + `data/my_profile.md` (proposal dựa vào đây).
3. (Nếu muốn agent thật) đặt `AIFOS_WORKER_ENGINE=claude_code`, cài & đăng nhập Claude Code CLI, trỏ `AIFOS_DELIVERY_ROOT` vào thư mục an toàn.
4. Bật hệ thống — chọn 1:
   - **Nhanh (1 lệnh):** `python scripts/start.py` — tự bật server + Scout, có preflight + health-check.
   - **Thủ công (2 terminal):** T1 `uvicorn app.main:app --port 8001` · T2 `python scripts/run_scouts.py` (hoặc `--once` để thử).
5. Khi có job đạt ROI → Telegram báo. Bấm **👍 Approve & Pitch**.
6. Nhận proposal → kiểm tra → bấm **🚀 Start Work**.
7. (claude_code + plan-gate) duyệt **PLAN.md** → agent làm → QA.
8. Nhận **DELIVERY_READY**: mở folder trong `AIFOS_DELIVERY_ROOT` để review. Vướng thì bấm **🔁 Làm lại**.
9. Hài lòng → bấm **✅ Nghiệm thu**, rồi gửi khách (thủ công).

---

## 10. Production (always-on, bền)

```powershell
copy .env.example .env   # điền key + AIFOS_ADMIN_PASSWORD
docker compose up --build
```

Khởi động 4 service: `api` (uvicorn 8000), `worker` (Arq), `redis`, `postgres`. Compose tự đặt `AIFOS_TASK_BACKEND=arq`, chạy `alembic upgrade head` trước khi serve. Ưu điểm: job vào hàng đợi Redis, sống sót khi restart; lúc khởi động API tự cứu các job đang dở (`app/services/recovery.py`).

> Sau khi đổi schema/pull code: `alembic upgrade head`. Tạo revision mới: `alembic revision --autogenerate -m "..."`.

---

## 11. Kiểm tra sức khỏe & bảo trì

| Việc | Lệnh / Endpoint |
|---|---|
| Bật nhanh (server + scout) | `python scripts/start.py` |
| Liveness | `GET /healthz` |
| Deep check (DB, Redis nếu arq) | `GET /health/deep` |
| Metrics (khi bật) | `GET /metrics` + `AIFOS_METRICS_ENABLED=true` |
| Admin UI | `http://127.0.0.1:8001/admin` |
| API docs | `http://127.0.0.1:8001/docs` |
| Chạy test | `python -m pytest -q` |
| Lint | `python -m ruff check app tests` |
| Thử scout không ingest | `python scripts/run_scouts.py --dry-run` |

---

## 12. Khắc phục sự cố thường gặp

| Triệu chứng | Nguyên nhân & cách xử |
|---|---|
| Scout chạy nhưng API không nhận job | Sai cổng — API phải ở đúng `AIFOS_SCOUT_API_BASE_URL` (mặc định 8001) |
| Telegram không có thông báo | Thiếu `AIFOS_TELEGRAM_BOT_TOKEN`/`DEFAULT_CHAT_ID`; hoặc chưa nhắn cho bot trước khi lấy chat id |
| Bấm nút Telegram không phản hồi | Webhook chưa đăng ký (mode webhook) hoặc máy tắt (mode polling). Kiểm tra webhook ở `/admin` |
| Job bị “mock”, kết quả vô nghĩa | Chưa điền `GEMINI_API_KEY`; hệ thống dùng LLM giả khi `AIFOS_ALLOW_MOCK_LLM=true` |
| Ingest trả 422 | `source` không nằm trong allowlist (`app/schemas.py`) |
| Engine claude_code báo “CLI not found” | Chưa cài/đăng nhập Claude Code CLI; kiểm tra `AIFOS_CLAUDE_BIN` |
| Threads chỉ trả tài khoản Meta | Chưa được App Review (Advanced Access). Dùng làn nhanh RSS trong lúc chờ |
| Agent làm xong nhưng kẹt không thao tác tiếp được | Dùng nút **🔁 Làm lại** trên tin nhắn; hoặc gọi `POST /api/v1/jobs/{id}/start-work` |

---

## 13. Checklist “đi vào hoạt động thật”

- [ ] `GEMINI_API_KEY` đã điền (hết chế độ mock).
- [ ] `AIFOS_TELEGRAM_BOT_TOKEN` + `DEFAULT_CHAT_ID` đã điền, đã nhận được tin test.
- [ ] Chọn `AIFOS_TELEGRAM_MODE` (polling cho laptop / webhook cho server) và đã verify nút bấm phản hồi.
- [ ] API chạy ở **cổng 8001** (hoặc đã sửa `AIFOS_SCOUT_API_BASE_URL`).
- [ ] `portfolio/operator_portfolio.md` + `data/my_profile.md` đã cập nhật đúng năng lực bạn.
- [ ] Bật ≥1 nguồn scout (RSS sẵn có là đủ để bắt đầu); chạy `--dry-run` thấy có job.
- [ ] (Nếu agent thật) `AIFOS_WORKER_ENGINE=claude_code`, Claude CLI đã đăng nhập, `AIFOS_DELIVERY_ROOT` trỏ thư mục an toàn.
- [ ] Đã chạy thử trọn 1 job: Approve → Proposal → Start Work → Delivery → Nghiệm thu.
- [ ] (Production) `docker compose up`, đặt `AIFOS_ADMIN_PASSWORD`.

---

*Tài liệu cập nhật theo nhánh `feature/agentic-worker`. Chi tiết kỹ thuật bổ sung xem `README.md`.*
