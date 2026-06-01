import os

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings


@pytest.fixture(scope="session")
def client(tmp_path_factory: pytest.TempPathFactory) -> TestClient:
    tmp_path = tmp_path_factory.mktemp("aifos")
    db_path = tmp_path / "test.db"
    portfolio_path = tmp_path / "portfolio.md"
    workspace_path = tmp_path / "workspaces"
    portfolio_path.write_text(
        "# Portfolio\n\n## Featured Projects\n- URL: https://example.com/relevant-project\n",
        encoding="utf-8",
    )

    os.environ["AIFOS_DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    os.environ["AIFOS_PORTFOLIO_MARKDOWN_PATH"] = str(portfolio_path)
    os.environ["AIFOS_WORKSPACE_STORAGE_PATH"] = str(workspace_path)
    os.environ["AIFOS_TELEGRAM_WEBHOOK_SECRET"] = "super-secret"
    os.environ["AIFOS_ALLOW_MOCK_LLM"] = "true"
    os.environ["AIFOS_TELEGRAM_BOT_TOKEN"] = ""
    os.environ["AIFOS_TELEGRAM_DEFAULT_CHAT_ID"] = ""
    os.environ["AIFOS_OPENAI_API_KEY"] = ""
    os.environ["AIFOS_ANTHROPIC_API_KEY"] = ""
    os.environ["GEMINI_API_KEY"] = ""
    os.environ["AIFOS_GEMINI_API_KEY"] = ""

    get_settings.cache_clear()

    from app.main import create_app

    application = create_app()
    with TestClient(application) as test_client:
        yield test_client

    get_settings.cache_clear()
