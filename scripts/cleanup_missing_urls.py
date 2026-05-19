from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse

from semantic_site_rag.config import get_settings
from semantic_site_rag.crawler import SiteCrawler
from semantic_site_rag.database import RagDatabase


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mark URLs missing from current sitemap.")
    parser.add_argument("--sitemap", action="append", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    crawler = SiteCrawler(settings)
    db = RagDatabase(settings)
    sitemap_urls = set(crawler.fetch_many_sitemaps(args.sitemap))
    known_urls = set(db.list_page_urls())
    missing = sorted(known_urls - sitemap_urls)
    db.mark_missing_from_sitemap(missing)
    print(f"Marked {len(missing)} URLs as missing from sitemap")


if __name__ == "__main__":
    main()

