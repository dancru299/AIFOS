from email.message import EmailMessage

from app.services.scouts.gmail_fetcher import parse_job_alert_email
from app.services.scouts.reddit import parse_reddit_child
from app.services.scouts.rss import parse_rss_entry
from app.services.scouts.upwork import parse_upwork_entry


class Entry:
    title = "Need Next.js Tailwind Landing Page"
    link = "https://www.upwork.com/jobs/_123"
    id = "upwork-123"
    summary = "Budget: $400 Fixed Price Country: United States Need a landing page from Figma."
    published = "Sun, 31 May 2026 10:00:00 +0000"
    content = []


def test_parse_upwork_entry_extracts_job_fields():
    job = parse_upwork_entry(Entry(), "https://example.com/rss")

    assert job is not None
    assert job.source == "upwork"
    assert job.external_url == "https://www.upwork.com/jobs/_123"
    assert job.budget_raw == "$400"
    assert job.client_location == "United States"


def test_parse_open_rss_entry_detects_source():
    job = parse_rss_entry(Entry(), "https://weworkremotely.com/categories/remote-programming-jobs.rss")

    assert job is not None
    assert job.source == "weworkremotely"
    assert job.budget_raw == "$400"


def test_parse_gmail_upwork_alert_extracts_job_links():
    message = EmailMessage()
    message["Subject"] = "Upwork Job Alert: Python automation"
    message["Date"] = "Sun, 31 May 2026 10:00:00 +0000"
    message["Message-ID"] = "<alert-1@example.com>"
    message.set_content("Plain fallback")
    message.add_alternative(
        """
        <html>
          <body>
            <table>
              <tr>
                <td>
                  <a href="https://www.upwork.com/jobs/~012345">Python scraping automation</a>
                  <p>Budget: $500</p>
                  <p>Client Location: United States</p>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """,
        subtype="html",
    )

    jobs = parse_job_alert_email(message)

    assert len(jobs) == 1
    assert jobs[0].source == "upwork"
    assert jobs[0].title == "Python scraping automation"
    assert jobs[0].external_url == "https://www.upwork.com/jobs/~012345"
    assert jobs[0].budget_raw == "$500"
    assert jobs[0].client_location == "United States"
    assert jobs[0].client_metadata["collector"] == "gmail_inbox"


def test_parse_gmail_linkedin_alert_canonicalizes_redirect_links():
    message = EmailMessage()
    message["Subject"] = "LinkedIn Job Alert: React developer"
    message.set_content(
        "React Frontend Developer in Canada https://www.linkedin.com/jobs/view/1234567890/?trackingId=abc&utm_source=email"
    )

    jobs = parse_job_alert_email(message)

    assert len(jobs) == 1
    assert jobs[0].source == "linkedin"
    assert jobs[0].external_url == "https://www.linkedin.com/jobs/view/1234567890/"
    assert jobs[0].client_location == "Canada"


def test_parse_reddit_child_extracts_job_fields():
    child = {
        "data": {
            "id": "abc123",
            "title": "[Hiring] Python scraping script - $500",
            "selftext": "Need a Python scraper for real estate listings. US client.",
            "permalink": "/r/forhire/comments/abc123/hiring_python_scraping/",
            "author": "client_user",
            "created_utc": 1780211502,
            "score": 4,
            "num_comments": 1,
        }
    }

    job = parse_reddit_child(child, "forhire")

    assert job is not None
    assert job.source == "reddit"
    assert job.budget_raw == "$500"
    assert job.client_location == "United States"
    assert job.client_metadata["subreddit"] == "forhire"
