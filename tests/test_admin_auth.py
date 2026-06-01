import os

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings


@pytest.fixture
def admin_client(client):
    """A TestClient whose app has an admin password configured."""
    os.environ["AIFOS_ADMIN_USERNAME"] = "admin"
    os.environ["AIFOS_ADMIN_PASSWORD"] = "s3cret"
    get_settings.cache_clear()

    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client

    os.environ.pop("AIFOS_ADMIN_USERNAME", None)
    os.environ.pop("AIFOS_ADMIN_PASSWORD", None)
    get_settings.cache_clear()


def test_admin_rejected_without_credentials(admin_client):
    response = admin_client.get("/admin")
    assert response.status_code == 401


def test_admin_rejected_with_wrong_credentials(admin_client):
    response = admin_client.get("/admin", auth=("admin", "wrong"))
    assert response.status_code == 401


def test_admin_allowed_with_valid_credentials(admin_client):
    response = admin_client.get("/admin", auth=("admin", "s3cret"))
    assert response.status_code == 200
    assert "AI-FOS Settings" in response.text
