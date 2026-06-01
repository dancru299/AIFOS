[ Scout Agent ] ──> (Scrapes/Listens to Upwork RSS, Reddit, X)
│
▼
[ Analyst Agent ] ──> (Filters out bad clients, computes ROI Score)
│
├─► Score < 7.0  ──> [Archived/Discarded]
└─► Score >= 7.0 ──> [Bangs Telegram Notification to Human]
│
▼
(Human Approves)
│
▼
[ Proposal Agent ] ──> (Generates short, hyper-personalized pitch + price)
│
▼
(Human Sends to Client)
│
▼
[Client Accepts Job]
│
▼
[ PM Agent ] ──> (Generates PRD, Milestone Roadmap, Task Breakdown)
│
▼
[ Worker Agent ] ──> (Executes code snippets, crawls data, drafts content)
│
▼
[ QA Agent ] ──> (Reviews against PRD checklist, checks code/grammar syntax)
│
▼
[ Delivery Agent ] ──> (Packages outputs into Markdown, ZIP, GitHub PR, or PDF)
│
▼
[ Human Operator ] ──> (One-click Approval & Delivery to Client)


---

## 5. Core Features (Agent-by-Agent Specification)

### 5.1 Scout Agent (The Hunter)
* **Functional Requirement:** Continuous ingestion of job feeds across 3 main vectors: Upwork (RSS), Reddit API (Subreddits: `r/forhire`, `r/freelance_forhire`), and X/Twitter Filtered Stream (Keywords: "looking for a dev", "need a landing page").
* **Frequency:** Every 15 minutes (configurable cron).
* **Output:** Normalized Job Objects containing: Title, Source URL, Description Raw Text, Budget, Client Metadata.

### 5.2 Analyst Agent (The Gatekeeper)
* **Functional Requirement:** Evaluates normalized jobs against an explicit algorithmic scoring prompt.
* **Filtering Logic (Strict Guardrails):**
    * *Good Patterns:* Fixed-price landing pages, blog post copywriting, Python scraping, standardized CRUD backend setups.
    * *Bad Patterns (Instant Drop):* Vague multi-stakeholder requirements ("build a platform like Uber"), brand design projects, complex mobile app architectures with low budgets.
* **Scoring Formula Prompting:** Uses `gpt-4o-mini` to evaluate a score from 1-10 based on region profile, payment verification status, and tech-stack clarity. If Score $\geq$ 7.0, triggers a Telegram Bot webhook containing inline interactive buttons `[Approve]` / `[Reject]`.

### 5.3 Proposal Assistant Agent (The Closer)
* **Functional Requirement:** Triggered upon human approval from Telegram. Ingests the job context and the Operator’s master portfolio data (e.g., contents from `dancru.cloud`).
* **Tone Framework:** Short, direct, completely devoid of AI introductory fluff ("Dear hiring manager", "I hope this finds you well"). Immediately addresses the problem, proposes an architectural stack, embeds a past project URL link, and finishes with an open conversational hook question.

### 5.4 PM & Worker Agent (The Engine)
* **PM Module:** Converts accepted proposals into structured Markdown tasks, decomposing requirements into atomic micro-tasks.
* **Worker Module:** Operates using **Claude 3.5 Sonnet** split-execution loops:
    * *Content Track:* Generates SEO outline mapping top competitors, drafts native-level copy.
    * *Code Track:* Writes modular code files or isolated components (Next.js components, Laravel controllers), avoiding massive system rewrites to minimize hallucination limits.

### 5.5 QA & Delivery Agent (The Polisher)
* **QA Module:** Compiles the generated asset and runs automated lint tests (for code) or semantic checks (for text).
* **Delivery Module:** Structures assets into final formats ready for client dispatch: cleanly organized ZIP archives, programmatic GitHub Pull Requests, or formatted Markdown/PDF documents.

---

## 6. Tech Stack & Architecture

To optimize for extreme velocity, minimal API latency, and zero UI bloat during Phase 1-2, the architectural setup relies on a split headless pipeline:

* **Agent Core Logic:** Python 3.11+ using **CrewAI** or **LangGraph**. Python provides superior native library support for text processing and AI agent state management loops.
* **Fast API Layer:** **FastAPI** (Python) providing RESTful endpoints to manage agent execution states and handle inbound webhooks from Telegram.
* **Data Tier:** **SQLite** for local development and MVP storage simplicity, upgrading to **Supabase (PostgreSQL)** when transitioning to production.
* **LLM Model Matrix:**
    * `Claude 3.5 Sonnet API` (Anthropic): Dedicated to high-reasoning tasks: Proposal generation, Worker execution (code/copywriting).
    * `GPT-4o-mini API` (OpenAI): Dedicated to low-cost structured filtering: Scout parsing, Analyst scoring, QA formatting validation.
* **Notification Node:** **Telegram Bot API** with interactive inline keypads acting as the absolute master control layer.

---

## 7. Database Schema (SQL Core Blueprint)

```sql
-- Jobs table storing inbound items from Scout Agent
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL, -- 'upwork', 'reddit', 'x'
    external_url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description_raw TEXT NOT NULL,
    budget_raw TEXT,
    client_location TEXT,
    roi_score REAL,
    analysis_reasoning TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'proposal_sent'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Active tasks generated by PM Agent upon project win
CREATE TABLE project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT REFERENCES jobs(id),
    task_title TEXT NOT NULL,
    task_scope TEXT NOT NULL, -- 'code', 'writing', 'scraping'
    generated_output TEXT,
    qa_status TEXT DEFAULT 'unreviewed', -- 'unreviewed', 'passed', 'failed'
    qa_logs TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
## 8. API Design (Key Endpoints)

### 8.1 Inbound Scraper Ingestion
- **Endpoint:** `POST /api/v1/jobs/ingest`
- **Description:** Receives normalized job payloads from Scout scrapers.
- **Request example:**
```json
{
    "source": "upwork",
    "external_url": "https://www.upwork.com/jobs/_123",
    "title": "Need Next.js Tailwind Landing Page",
    "description_raw": "Looking for an expert to convert Figma to responsive code..."
}
```
- **Response:** `202 Accepted` (dispatches asynchronous processing to Analyst Agent)

### 8.2 Telegram Webhook Receiver
- **Endpoint:** `POST /api/v1/telegram/webhook`
- **Description:** Receives Telegram callback_query payloads from inline button presses (e.g., `[Approve]` / `[Reject]`) and forwards the decision to the backend for further processing.

## 9. User Interface (UI) Layout Strategy

**Headless Telegram UI (Phase 1-2)**

To achieve extreme execution efficiency, no web dashboard is built initially. The smartphone's Telegram interface acts as the master dashboard via interactive rich-text payloads. Example alert card:

```text
┌────────────────────────────────────────────────────────┐
│ 📡 NEW HIGH-ROI JOB DETECTED [Score: 8.5/10]          │
│ ────────────────────────────────────────────────────── │
│ 📍 Source: Upwork (Fixed Price)                        │
│ 💼 Title: Build Scraping Bot for Real Estate Listings   │
│ 💵 Budget: $400 | Client Country: United States        │
│                                                        │
│ 🔍 ANALYST METRICS:                                    │
│ - Tech Stack Match: 95% (Python/Scraping)              │
│ - Scope Risk: Low (Clear API/Target specified)         │
│                                                        │
│ 📝 REASONING: Highly structured input data. Target site│
│ has no cloudflare protection. High profit margin.      │
│ ────────────────────────────────────────────────────── │
│       [ 👍 APPROVE & PITCH ]     [ 👎 DISMISS ]        │
└────────────────────────────────────────────────────────┘
```

## 10. Implementation Roadmap & MVP Scope

### 10.1 MVP Scope (Phase 1 & Phase 2)
- Automated scanning of Upwork RSS and Reddit (`/r/forhire`).
- LLM processing to extract text, filter bad-pattern keywords, and compute a 1–10 priority score.
- Send formatted alert cards to the operator's Telegram with inline confirmation triggers.
- Generate a concise outreach proposal text block for manual copy-paste upon approval.

### 10.2 Future Horizon Roadmap
- **Phase 3 (Work Planner):** Auto-parse accepted requirements into atomic local `.md` boards and microtask breakdowns.
- **Phase 4 (Worker Integration):** Hook sandboxed filesystem executions for code/data agents producing modular files.
- **Phase 5 (Full Pipeline Delivery):** Integrate with GitHub to push branches and open PRs directly from agent cycles.

## 11. Critical System Risks & Mitigation Strategy

### 11.1 Scraper Deprecation & Rate Limiting
- **Risk:** Major platforms change UIs or ban IPs used for continuous scraping.
- **Mitigation:** Focus on stable sources (Upwork RSS) and official, rate-compliant APIs (Reddit).

### 11.2 Pitch Quality Decay ("AI Odor")
- **Risk:** Boilerplate proposals get rejected on visible platforms.
- **Mitigation:** Enforce strict prompt rules banning passive phrases and long intros; cap outreach length to 100–120 words.

### 11.3 AI Code Hallucinations
- **Risk:** Generated code references nonexistent methods or broken dependencies.
- **Mitigation:** Restrict Worker Agent to small, verifiable units (single-file scripts, isolated utilities) and require manual QA checks.


Dưới vai trò là một **Product Manager kiêm Tech Lead**, mình đã thiết kế và hoàn thiện tài liệu **PRD (Product Requirement Document)** chi tiết cho hệ thống **AI Freelancer Operating System (AI-FOS)**. 

Bản PRD này được viết theo hướng tiếp cận thực chiến tối đa, tinh gọn phần UI ở giai đoạn đầu để tập trung 100% tài nguyên vào lõi xử lý của Agent và giải quyết bài toán nguồn việc mang lại dòng tiền ngay lập tức.

File tài liệu định dạng Markdown đã được tạo thành công:
[file-tag: code-generated-file-0-1780211502094392868]

Dưới đây là tóm tắt các điểm cốt lõi và các **Giả định thiết kế (Assumptions)** quan trọng được đưa vào tài liệu:

### 1. Chiến lược "Headless UI" cho MVP (Giai đoạn 1 & 2)
* **Giả định:** Việc xây dựng một Dashboard bằng Web (React/Next.js/Laravel) ở Phase 1 là **lãng phí thời gian** và làm giảm tốc độ thực thi của bạn. 
* **Giải pháp:** Biến **Telegram thành giao diện quản trị duy nhất**. Scout Agent quét việc -> Analyst Agent chấm điểm -> Gửi thẻ thông tin dạng Rich-text kèm nút bấm Inline `[Approve]` / `[Reject]` thẳng vào điện thoại của bạn. Bạn duyệt việc và nhận Proposal ngay khi đang đi dạo hoặc uống cafe.

### 2. Tiêu chuẩn lọc Job Nghiêm ngặt (The Guardrails)
* Hệ thống phân loại rõ hai nhóm dữ liệu đầu vào thông qua Prompt của `gpt-4o-mini`:
    * **Job Tốt (Chấp nhận):** Landing page, blog post, cào dữ liệu bằng Python, cấu trúc CRUD đơn giản.
    * **Job Xấu (Bỏ qua ngay):** Yêu cầu thiết kế thương hiệu, hệ thống phức tạp nhiều bên tham gia, ngân sách thấp nhưng mô tả mơ hồ.

### 3. Công thức Tối ưu Chi phí API & Chất lượng Đầu ra
* **Tối ưu chi phí:** Dùng `gpt-4o-mini` cho các tác vụ lặp đi lặp lại có dung lượng text lớn (Cào dữ liệu từ Scout, Đọc mô tả và Chấm điểm ROI ở Analyst).
* **Tối ưu chất lượng:** Chỉ kích hoạt **Claude 3.5 Sonnet** (Model đỉnh nhất hiện tại về code và viết lách tự nhiên) cho các tác vụ tạo ra tiền: Viết Proposal (Phase 2) và Sinh mã nguồn/Nội dung bài viết (Phase 4).

### 4. Thiết kế Database Tinh gọn (Schema Blueprint)
* Sử dụng hệ cơ sở dữ liệu gọn nhẹ để lưu trữ lịch sử Job, chấm điểm ROI, lý do lựa chọn (Reasoning) và trạng thái của các Task để đảm bảo AI Agent có thể truy vết và tự kiểm tra (QA) dựa trên Checklist ban đầu.

---