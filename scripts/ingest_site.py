from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import json
import time
from pathlib import Path

from semantic_site_rag.config import get_settings
from semantic_site_rag.crawler import SiteCrawler
from semantic_site_rag.database import RagDatabase
from semantic_site_rag.embeddings import EmbeddingClient
from semantic_site_rag.ingest import ingest_page


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a website into Supabase RAG tables.")
    parser.add_argument("--sitemap", action="append", default=[], help="Sitemap URL. Can be passed several times.")
    parser.add_argument("--url", action="append", default=[], help="Single URL. Can be passed several times.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit for tests.")
    parser.add_argument("--force", action="store_true", help="Force re-embedding even if content did not change.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    crawler = SiteCrawler(settings)
    db = RagDatabase(settings)
    embedder = EmbeddingClient(settings)

    urls = set(args.url)
    if args.sitemap:
        urls.update(crawler.fetch_many_sitemaps(args.sitemap))
    ordered_urls = sorted(urls)
    if args.limit:
        ordered_urls = ordered_urls[: args.limit]

    report = {"processed": 0, "changed": 0, "unchanged": 0, "failed": 0, "items": []}
    for url in ordered_urls:
        try:
            result = ingest_page(url, settings, db, embedder, force=args.force)
            report["processed"] += 1
            report[result["status"]] = report.get(result["status"], 0) + 1
            report["items"].append(result)
            print(f"{result['status']}: {result['url']}")
        except Exception as exc:
            report["failed"] += 1
            report["items"].append({"url": url, "status": "failed", "error": str(exc)})
            print(f"failed: {url} - {exc}")
        time.sleep(settings.crawl_delay_seconds)

    Path("reports").mkdir(exist_ok=True)
    Path("reports/ingest_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "items"}, indent=2))


if __name__ == "__main__":
    main()

