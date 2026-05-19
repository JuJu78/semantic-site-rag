from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from semantic_site_rag.config import get_settings
from semantic_site_rag.crawler import SiteCrawler
from semantic_site_rag.database import RagDatabase
from semantic_site_rag.embeddings import EmbeddingClient
from semantic_site_rag.ingest import ingest_page


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Incrementally refresh Supabase RAG tables from sitemap URLs.")
    parser.add_argument("--sitemap", action="append", required=True, help="Sitemap URL. Can be passed several times.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit for tests.")
    parser.add_argument("--mark-missing", action="store_true", default=True, help="Mark URLs absent from sitemap.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    crawler = SiteCrawler(settings)
    db = RagDatabase(settings)
    embedder = EmbeddingClient(settings)

    sitemap_urls = crawler.fetch_many_sitemaps(args.sitemap)
    if args.limit:
        sitemap_urls = sitemap_urls[: args.limit]

    known_urls = set(db.list_page_urls())
    sitemap_set = set(sitemap_urls)
    missing = sorted(known_urls - sitemap_set)
    if args.mark_missing and missing:
        db.mark_missing_from_sitemap(missing)

    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "sitemap_url_count": len(sitemap_urls),
        "processed": 0,
        "changed": 0,
        "unchanged": 0,
        "failed": 0,
        "missing_from_sitemap": len(missing),
        "items": [],
    }

    for url in sitemap_urls:
        try:
            result = ingest_page(url, settings, db, embedder)
            report["processed"] += 1
            report[result["status"]] = report.get(result["status"], 0) + 1
            report["items"].append(result)
            print(f"{result['status']}: {result['url']}")
        except Exception as exc:
            report["failed"] += 1
            report["items"].append({"url": url, "status": "failed", "error": str(exc)})
            print(f"failed: {url} - {exc}")
        time.sleep(settings.crawl_delay_seconds)

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    Path("reports").mkdir(exist_ok=True)
    report_path = Path("reports") / f"refresh_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "items"}, indent=2))


if __name__ == "__main__":
    main()

