from app.core.config import Settings


def test_settings_reads_bare_gemini_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.delenv("AIFOS_GEMINI_API_KEY", raising=False)

    settings = Settings()

    assert settings.gemini_api_key == "test-gemini-key"


def test_settings_defaults_to_open_rss_feeds(monkeypatch):
    monkeypatch.delenv("AIFOS_RSS_FEED_URLS", raising=False)

    settings = Settings()

    assert "weworkremotely.com" in settings.rss_feed_urls
    assert "remoteok.com" in settings.rss_feed_urls
    assert len(settings.parsed_rss_feed_urls) == 2


def test_settings_detects_gmail_inbox_when_credentials_exist(monkeypatch):
    monkeypatch.setenv("AIFOS_GMAIL_EMAIL", "operator@gmail.com")
    monkeypatch.setenv("AIFOS_GMAIL_APP_PASSWORD", "app-password")

    settings = Settings()

    assert settings.gmail_inbox_enabled is True
    assert settings.parsed_gmail_alert_subjects == ["Upwork Job Alert", "LinkedIn Job Alert"]
