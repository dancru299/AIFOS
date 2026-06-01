import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Configure the environment at import time — BEFORE any app module is imported —
# so app.db.engine (built once at import) binds to a throwaway test database
# rather than the real ./data/aifos.db. Test modules that import app.* at the top
# level rely on this ordering.
_TMP_DIR = Path(tempfile.mkdtemp(prefix="aifos-test-"))
_DB_PATH = _TMP_DIR / "test.db"
_PORTFOLIO_PATH = _TMP_DIR / "portfolio.md"
_PORTFOLIO_PATH.write_text(
    "# Portfolio\n\n## Featured Projects\n- URL: https://example.com/relevant-project\n",
    encoding="utf-8",
)

os.environ["AIFOS_DATABASE_URL"] = f"sqlite:///{_DB_PATH.as_posix()}"
os.environ["AIFOS_PORTFOLIO_MARKDOWN_PATH"] = str(_PORTFOLIO_PATH)
os.environ["AIFOS_WORKSPACE_STORAGE_PATH"] = str(_TMP_DIR / "workspaces")
os.environ["AIFOS_TELEGRAM_WEBHOOK_SECRET"] = "super-secret"
os.environ["AIFOS_ALLOW_MOCK_LLM"] = "true"
os.environ["AIFOS_TASK_BACKEND"] = "background"
os.environ["AIFOS_TELEGRAM_BOT_TOKEN"] = ""
os.environ["AIFOS_TELEGRAM_DEFAULT_CHAT_ID"] = ""
os.environ["AIFOS_OPENAI_API_KEY"] = ""
os.environ["AIFOS_ANTHROPIC_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["AIFOS_GEMINI_API_KEY"] = ""


@pytest.fixture(scope="session")
def client() -> TestClient:
    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.main import create_app

    application = create_app()
    with TestClient(application) as test_client:
        yield test_client

    get_settings.cache_clear()
