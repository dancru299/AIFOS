"""Run the Telegram long-poller as a standalone process.

Use this when the API runs in webhook/none mode but you still want to receive
button taps without a public URL (e.g. behind NAT). It shares the same database
and pipeline as the API. Prefer setting AIFOS_TELEGRAM_MODE=polling to run the
poller inside the API process instead.

    python scripts/run_telegram_poller.py
"""

import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db import init_db
from app.services.telegram_poller import run_poller


def main() -> int:
    configure_logging(get_settings().json_logs)
    init_db()
    try:
        asyncio.run(run_poller())
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Poller stopped by user")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
