import argparse
import asyncio
import logging
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.services.scouts.runner import ScoutRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AI-FOS Scout Agent.")
    parser.add_argument("--once", action="store_true", help="Run a single scout cycle and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch jobs but do not submit them to the ingest API.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    settings = get_settings()
    runner = ScoutRunner(settings)

    if args.dry_run:
        jobs = asyncio.run(runner.fetch_all())
        print(f"fetched={len(jobs)}")
        for job in jobs[:10]:
            print(f"- [{job.source}] {job.title} -> {job.external_url}")
        return 0

    if args.once:
        result = asyncio.run(runner.run_once())
        print(result)
        return 0

    asyncio.run(runner.run_forever())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
