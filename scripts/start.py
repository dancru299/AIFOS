"""One-command launcher for AI-FOS.

Runs a preflight on the important env keys (LLM, Telegram bot token + chat id,
scout sources, worker engine), starts the FastAPI server on the right port, waits
until it is healthy, runs the deep health check, optionally pings your Telegram
chat, then starts the Scout (job hunter) so jobs actually start flowing — all
from a single command:

    python scripts/start.py

Useful flags:
    --port N       Override the port (default: parsed from AIFOS_SCOUT_API_BASE_URL, else 8001).
    --reload       Start uvicorn with --reload (auto-restart on code edits).
    --no-scouts    Run the server only; do not start the job-hunting Scout.
    --no-ping      Do not send the Telegram startup ping.
    --timeout N    Seconds to wait for the server to become healthy (default 30).

Press Ctrl+C to stop everything (server + scout).
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

# Emoji status marks below break on Windows when stdout is piped (cp1252). Force
# UTF-8 with replacement so the launcher never crashes on its own output.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402

OK = "✅"
WARN = "⚠️ "
BAD = "❌"


def _mark(ok: bool, warn: bool = False) -> str:
    if ok:
        return OK
    return WARN if warn else BAD


def preflight(settings) -> bool:
    """Print a status line per important key. Returns True if the server can do real work."""
    print("\n=== Kiểm tra cấu hình (.env) ===")

    # --- LLM (cần để hết chế độ mock) ---
    llm_keys = {
        "Gemini": settings.gemini_api_key,
        "OpenAI": settings.openai_api_key,
        "Anthropic": settings.anthropic_api_key,
    }
    present = [name for name, key in llm_keys.items() if key]
    if present:
        print(f"{OK} LLM key: {', '.join(present)} (chấm ROI + soạn proposal thật)")
        llm_ok = True
    elif settings.allow_mock_llm:
        print(f"{WARN}LLM key: CHƯA có → chạy LLM giả (mock). Điền GEMINI_API_KEY để có kết quả thật.")
        llm_ok = False
    else:
        print(f"{BAD} LLM key: CHƯA có và mock đã tắt → pipeline sẽ lỗi. Điền GEMINI_API_KEY.")
        llm_ok = False

    # --- Telegram ---
    has_token = bool(settings.telegram_bot_token)
    has_chat = bool(settings.telegram_default_chat_id)
    print(f"{_mark(has_token)} Telegram bot token: {'đã set' if has_token else 'CHƯA set'}")
    if has_chat:
        print(f"{OK} Telegram chat id: {settings.telegram_default_chat_id}")
    else:
        print(f"{BAD} Telegram chat id: CHƯA set → chạy scripts/get_telegram_chat_id.py để lấy.")
    print(f"   ↳ chế độ nhận nút bấm: AIFOS_TELEGRAM_MODE={settings.telegram_mode}")

    # --- Scout sources ---
    sources = []
    if settings.parsed_rss_feed_urls:
        sources.append(f"RSS({len(settings.parsed_rss_feed_urls)})")
    if settings.parsed_reddit_subreddits:
        sources.append(f"Reddit({len(settings.parsed_reddit_subreddits)})")
    if settings.gmail_inbox_enabled:
        sources.append("Gmail")
    if settings.threads_enabled:
        sources.append("Threads")
    print(f"{_mark(bool(sources), warn=True)} Nguồn săn job: {', '.join(sources) if sources else 'CHƯA bật nguồn nào'}")

    # --- Worker engine ---
    engine = settings.worker_engine
    if engine == "claude_code":
        from shutil import which

        cli_ok = which(settings.claude_bin) is not None
        print(f"{_mark(cli_ok)} Worker engine: claude_code (Claude CLI '{settings.claude_bin}': {'tìm thấy' if cli_ok else 'KHÔNG thấy trên PATH'})")
    else:
        print(f"{OK} Worker engine: {engine}")

    # --- Task backend ---
    backend = settings.task_backend
    extra = " (cần Redis chạy)" if backend.lower() == "arq" else " (zero-infra)"
    print(f"{OK} Task backend: {backend}{extra}")

    return llm_ok and has_token and has_chat


def resolve_host_port(settings, override_port: int | None) -> tuple[str, int]:
    """Keep the server port aligned with AIFOS_SCOUT_API_BASE_URL (scouts ingest there)."""
    parsed = urlparse(settings.scout_api_base_url)
    host = parsed.hostname or "127.0.0.1"
    port = override_port or parsed.port or 8001
    return host, port


def probe_health(base_url: str, timeout: float = 2.0) -> dict | None:
    try:
        resp = httpx.get(f"{base_url}/healthz", timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except httpx.HTTPError:
        return None
    return None


def wait_until_healthy(base_url: str, timeout_s: int) -> bool:
    print(f"\nĐợi server sẵn sàng tại {base_url} (tối đa {timeout_s}s)...", end="", flush=True)
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if probe_health(base_url) is not None:
            print(" sẵn sàng!")
            return True
        print(".", end="", flush=True)
        time.sleep(1.0)
    print(" quá thời gian chờ.")
    return False


def deep_health(base_url: str) -> None:
    try:
        resp = httpx.get(f"{base_url}/health/deep", timeout=5.0)
        data = resp.json()
        status = data.get("status")
        checks = ", ".join(f"{k}={v}" for k, v in data.get("checks", {}).items())
        mark = OK if status == "ok" else WARN
        print(f"{mark}Deep health: {status} ({checks})")
    except httpx.HTTPError as exc:
        print(f"{WARN}Deep health: không gọi được ({exc})")


def telegram_ping(settings) -> None:
    if not settings.telegram_enabled:
        print(f"{WARN}Bỏ qua ping Telegram (chưa đủ token + chat id).")
        return
    url = f"{settings.telegram_api_base}/bot{settings.telegram_bot_token}/sendMessage"
    text = "✅ AI-FOS đã khởi động và bot hoạt động. (tin nhắn test từ scripts/start.py)"
    try:
        resp = httpx.post(url, json={"chat_id": settings.telegram_default_chat_id, "text": text}, timeout=15.0)
        payload = resp.json()
        if payload.get("ok"):
            print(f"{OK} Đã gửi tin nhắn test tới Telegram (chat id {settings.telegram_default_chat_id} hợp lệ).")
        else:
            print(f"{BAD} Telegram từ chối tin nhắn: {payload.get('description')}")
    except httpx.HTTPError as exc:
        print(f"{BAD} Không gửi được tin nhắn Telegram: {exc}")


def _shutdown(procs: "list[tuple[str, subprocess.Popen]]") -> None:
    """Terminate every supervised child, force-kill any that ignore terminate()."""
    for _name, proc in procs:
        if proc.poll() is None:
            proc.terminate()
    for _name, proc in procs:
        if proc.poll() is None:
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Bật AI-FOS chỉ với 1 lệnh.")
    parser.add_argument("--port", type=int, default=None, help="Cổng server (mặc định lấy từ AIFOS_SCOUT_API_BASE_URL hoặc 8001).")
    parser.add_argument("--reload", action="store_true", help="Bật uvicorn --reload (tự khởi động lại khi sửa code).")
    parser.add_argument("--no-scouts", dest="scouts", action="store_false", help="Chỉ chạy server, không bật Scout đi săn job.")
    parser.add_argument("--no-ping", action="store_true", help="Không gửi tin nhắn test Telegram khi khởi động.")
    parser.add_argument("--timeout", type=int, default=30, help="Số giây chờ server khoẻ (mặc định 30).")
    args = parser.parse_args()

    settings = get_settings()
    real_ready = preflight(settings)
    host, port = resolve_host_port(settings, args.port)
    base_url = f"http://{host}:{port}"

    procs: list[tuple[str, subprocess.Popen]] = []

    # Start the API server unless one is already serving this port.
    existing = probe_health(base_url)
    if existing is not None:
        print(f"\n{WARN}Đã có server chạy sẵn tại {base_url} — không bật thêm tiến trình API mới.")
    else:
        print(f"\n=== Khởi động server: uvicorn app.main:app --host {host} --port {port}{' --reload' if args.reload else ''} ===")
        server_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", host, "--port", str(port)]
        if args.reload:
            server_cmd.append("--reload")
        # Same console/process group so Ctrl+C reaches children too (graceful shutdown).
        procs.append(("server", subprocess.Popen(server_cmd)))
        if not wait_until_healthy(base_url, args.timeout):
            print(f"{BAD} Server chưa khoẻ trong thời gian chờ. Xem log phía trên để biết lỗi.")
            _shutdown(procs)
            return 1

    print("\n=== Sẵn sàng ===")
    deep_health(base_url)
    if not args.no_ping:
        telegram_ping(settings)

    # Start the Scout once the API is reachable; it POSTs hunted jobs back to it.
    if args.scouts:
        every_min = max(settings.scout_interval_seconds // 60, 1)
        print(f"\n=== Khởi động Scout: run_scouts.py (săn job, lặp mỗi ~{every_min} phút) ===")
        procs.append(("scout", subprocess.Popen([sys.executable, str(ROOT / "scripts" / "run_scouts.py")])))
    else:
        print(f"\n{WARN}Scout TẮT (--no-scouts) — chưa có gì đi săn job. Chạy `python scripts/run_scouts.py` riêng khi cần.")

    print(f"\n  Admin UI : {base_url}/admin")
    print(f"  API docs : {base_url}/docs")
    print(f"  Health   : {base_url}/healthz")
    if not real_ready:
        print(f"\n{WARN}Một số key còn thiếu (xem phần kiểm tra trên) — vẫn chạy được nhưng chưa 'thật' hoàn toàn.")

    if not procs:
        # Server already up and scouts disabled: nothing for this script to supervise.
        print("\nKhông có tiến trình nào do script này quản lý — kết thúc (server cũ vẫn chạy).")
        return 0

    print(f"\nĐang chạy: {' + '.join(name for name, _ in procs)}. Nhấn Ctrl+C để dừng tất cả.\n")
    try:
        # Block until any supervised child exits (or Ctrl+C), then bring the rest down together.
        while all(proc.poll() is None for _, proc in procs):
            time.sleep(0.5)
        for name, proc in procs:
            if proc.poll() is not None:
                print(f"\n{WARN}Tiến trình '{name}' đã dừng (mã {proc.returncode}) — tắt các tiến trình còn lại.")
    except KeyboardInterrupt:
        print("\nĐang dừng...")
    finally:
        _shutdown(procs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
