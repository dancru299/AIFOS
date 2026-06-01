from pathlib import Path
from zipfile import ZipFile


def test_ingest_runs_analysis_pipeline(client):
    response = client.post(
        "/api/v1/jobs/ingest",
        json={
            "source": "upwork",
            "external_url": "https://www.upwork.com/jobs/_123",
            "title": "Need Next.js Tailwind Landing Page",
            "description_raw": "Need a clean fixed-price landing page from Figma using Tailwind.",
            "budget_raw": "$400 fixed",
            "client_location": "United States",
        },
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]

    job_response = client.get(f"/api/v1/jobs/{job_id}")
    assert job_response.status_code == 200
    payload = job_response.json()
    assert payload["status"] == "awaiting_human_review"
    assert payload["roi_score"] >= 7.0
    assert payload["is_good_job"] is True
    assert "Tailwind CSS" in payload["tech_stack"]
    assert "matched good pattern" in payload["analysis_reasoning"]


def test_webhook_rejects_invalid_secret(client):
    response = client.post(
        "/api/v1/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
        json={},
    )
    assert response.status_code == 403


def test_admin_page_renders_provider_controls(client):
    response = client.get("/admin")

    assert response.status_code == 200
    assert "AI-FOS Settings" in response.text
    assert "analyst_provider" in response.text
    assert "proposal_provider" in response.text


def test_approve_moves_job_to_generating_then_ready(client):
    ingest_response = client.post(
        "/api/v1/jobs/ingest",
        json={
            "source": "reddit",
            "external_url": "https://reddit.com/r/forhire/comments/abc123",
            "title": "Python scraping job",
            "description_raw": "Looking for a Python scraping script for real estate listings.",
            "budget_raw": "$500",
            "client_location": "Canada",
        },
    )
    job_id = ingest_response.json()["job_id"]

    callback_payload = {
        "callback_query": {
            "id": "callback-1",
            "from": {"id": 123456},
            "data": f"approve_{job_id}",
            "message": {"message_id": 10, "chat": {"id": 999}},
        }
    }

    response = client.post(
        "/api/v1/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "super-secret"},
        json=callback_payload,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "generating_proposal"

    job_response = client.get(f"/api/v1/jobs/{job_id}")
    payload = job_response.json()
    assert payload["status"] == "proposal_ready"
    assert payload["proposal_text"]
    assert payload["proposal_price"]
    assert payload["proposal_timeline"]


def test_reject_moves_job_to_rejected(client):
    ingest_response = client.post(
        "/api/v1/jobs/ingest",
        json={
            "source": "upwork",
            "external_url": "https://www.upwork.com/jobs/_reject",
            "title": "Need landing page help with Tailwind",
            "description_raw": "Need a fixed-price landing page build from Figma using Tailwind.",
            "budget_raw": "$350 fixed",
            "client_location": "United States",
        },
    )
    job_id = ingest_response.json()["job_id"]

    callback_payload = {
        "callback_query": {
            "id": "callback-2",
            "from": {"id": 123456},
            "data": f"dismiss_{job_id}",
            "message": {"message_id": 11, "chat": {"id": 999}},
        }
    }

    response = client.post(
        "/api/v1/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "super-secret"},
        json=callback_payload,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

    job_response = client.get(f"/api/v1/jobs/{job_id}")
    assert job_response.json()["status"] == "rejected"


def test_start_work_creates_workspace_runs_qa_and_delivery(client):
    ingest_response = client.post(
        "/api/v1/jobs/ingest",
        json={
            "source": "reddit",
            "external_url": "https://reddit.com/r/forhire/comments/sandbox_scrape",
            "title": "Python scraping script for directory data",
            "description_raw": "Need a Python crawler that exports directory listings to JSON and CSV.",
            "budget_raw": "$600",
            "client_location": "United States",
        },
    )
    job_id = ingest_response.json()["job_id"]

    approve_response = client.post(
        "/api/v1/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "super-secret"},
        json={
            "callback_query": {
                "id": "callback-start-work-approve",
                "from": {"id": 123456},
                "data": f"approve_{job_id}",
                "message": {"message_id": 12, "chat": {"id": 999}},
            }
        },
    )
    assert approve_response.status_code == 200

    start_response = client.post(
        f"/api/v1/jobs/{job_id}/start-work",
        json={"task_scope": "scraping", "instructions": "Return JSON and CSV output examples."},
    )

    assert start_response.status_code == 202

    job_response = client.get(f"/api/v1/jobs/{job_id}")
    payload = job_response.json()
    assert payload["status"] == "delivery_ready"
    assert payload["workspace_path"]
    assert payload["delivery_path"]

    workspace_path = Path(payload["workspace_path"])
    delivery_path = Path(payload["delivery_path"])
    assert (workspace_path / "inputs" / "pm_brief.md").exists()
    assert (workspace_path / "src" / "crawler.py").exists()
    assert (workspace_path / "qa_reports" / "qa_report.json").exists()
    assert delivery_path.exists()

    with ZipFile(delivery_path) as archive:
        names = set(archive.namelist())
    assert "src/crawler.py" in names
    assert "qa_reports/qa_report.json" in names


def test_telegram_start_work_callback_creates_delivery(client):
    ingest_response = client.post(
        "/api/v1/jobs/ingest",
        json={
            "source": "upwork",
            "external_url": "https://www.upwork.com/jobs/_sandbox_web",
            "title": "Need Next.js landing page starter",
            "description_raw": "Need a fixed-price landing page from Figma using Tailwind.",
            "budget_raw": "$450 fixed",
            "client_location": "United States",
        },
    )
    job_id = ingest_response.json()["job_id"]

    client.post(
        "/api/v1/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "super-secret"},
        json={
            "callback_query": {
                "id": "callback-start-work-approve-web",
                "from": {"id": 123456},
                "data": f"approve_{job_id}",
                "message": {"message_id": 13, "chat": {"id": 999}},
            }
        },
    )

    response = client.post(
        "/api/v1/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "super-secret"},
        json={
            "callback_query": {
                "id": "callback-start-work-web",
                "from": {"id": 123456},
                "data": f"start_{job_id}",
                "message": {"message_id": 14, "chat": {"id": 999}},
            }
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    job_response = client.get(f"/api/v1/jobs/{job_id}")
    payload = job_response.json()
    assert payload["status"] == "delivery_ready"
    assert Path(payload["delivery_path"]).exists()
