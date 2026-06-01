import os

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_deep_health_ok(client):
    response = client.get("/health/deep")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"


def test_metrics_disabled_returns_404(client):
    assert client.get("/metrics").status_code == 404


@pytest.fixture
def metrics_client(client):
    os.environ["AIFOS_METRICS_ENABLED"] = "true"
    get_settings.cache_clear()

    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client

    os.environ.pop("AIFOS_METRICS_ENABLED", None)
    get_settings.cache_clear()


def test_metrics_enabled_exposes_prometheus(metrics_client):
    response = metrics_client.get("/metrics")
    assert response.status_code == 200
    assert "aifos_jobs" in response.text
