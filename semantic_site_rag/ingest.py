from __future__ import annotations

from datetime import datetime, timezone

from .chunking import chunk_text, estimate_tokens
from .config import Settings
from .crawler import CrawledPage, SiteCrawler
from .database import RagDatabase
from .embeddings import EmbeddingClient
from .hashing import sha256_text


def ingest_page(url: str, settings: Settings, db: RagDatabase, embedder: EmbeddingClient, force: bool = False) -> dict:
    crawler = SiteCrawler(settings)
    page = crawler.crawl(url)
    if not page.content:
        return {"url": url, "status": "failed", "error": "No readable content extracted"}

    content_hash = sha256_text(page.content)
    existing = db.get_page(page.final_url) or db.get_page(page.url)
    changed = force or not existing or existing.get("content_hash") != content_hash
    now = datetime.now(timezone.utc).isoformat()

    page_embedding = existing.get("embedding") if existing and not changed else embedder.embed(page.content[:12000])
    stored = db.upsert_page({
        "url": page.final_url,
        "canonical_url": page.final_url,
        "title": page.title,
        "description": page.description,
        "content": page.content,
        "content_hash": content_hash,
        "embedding": page_embedding,
        "status_code": page.status_code,
        "sitemap_present": True,
        "last_seen_in_sitemap_at": now,
        "last_crawled_at": now,
        "last_changed_at": now if changed else existing.get("last_changed_at") if existing else now,
        "updated_at": now,
    })

    if changed:
        chunks = []
        for index, chunk in enumerate(chunk_text(page.content, settings.chunk_size, settings.chunk_overlap)):
            chunks.append({
                "page_id": stored["id"],
                "url": page.final_url,
                "chunk_index": index,
                "content": chunk,
                "content_hash": sha256_text(chunk),
                "embedding": embedder.embed(chunk),
                "token_estimate": estimate_tokens(chunk),
            })
        db.replace_chunks(stored["id"], page.final_url, chunks)

    db.replace_links(page.final_url, page.links)
    return {"url": page.final_url, "status": "changed" if changed else "unchanged"}
