from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from semantic_site_rag.config import get_settings
from semantic_site_rag.database import RagDatabase
from semantic_site_rag.pagerank import compute_pagerank


def main() -> None:
    settings = get_settings()
    db = RagDatabase(settings)
    urls = db.list_page_urls()
    links = db.list_links()
    scores = compute_pagerank(urls, links)
    db.update_pagerank(scores)
    print(f"Updated PageRank for {len(scores)} URLs")


if __name__ == "__main__":
    main()

