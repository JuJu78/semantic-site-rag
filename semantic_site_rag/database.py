from __future__ import annotations

import ast
from datetime import datetime, timezone

from supabase import Client, create_client

from .config import Settings


class RagDatabase:
    def __init__(self, settings: Settings):
        self.client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    def get_page(self, url: str) -> dict | None:
        result = self.client.table("rag_pages").select("*").eq("url", url).limit(1).execute()
        return result.data[0] if result.data else None

    def upsert_page(self, payload: dict) -> dict:
        result = self.client.table("rag_pages").upsert(payload, on_conflict="url").execute()
        return result.data[0]

    def replace_chunks(self, page_id: int, url: str, chunks: list[dict]) -> None:
        self.client.table("rag_chunks").delete().eq("page_id", page_id).execute()
        if chunks:
            self.client.table("rag_chunks").insert(chunks).execute()

    def replace_links(self, source_url: str, links: list[dict]) -> None:
        self.client.table("rag_links").delete().eq("source_url", source_url).execute()
        internal_links = [link for link in links if link.get("is_internal")]
        if internal_links:
            self.client.table("rag_links").insert(internal_links).execute()

    def _select_all(self, table: str, columns: str, batch_size: int = 1000) -> list[dict]:
        rows: list[dict] = []
        start = 0
        while True:
            end = start + batch_size - 1
            result = self.client.table(table).select(columns).range(start, end).execute()
            batch = result.data or []
            rows.extend(batch)
            if len(batch) < batch_size:
                break
            start += batch_size
        return rows

    def list_page_urls(self) -> list[str]:
        return [row["url"] for row in self._select_all("rag_pages", "url")]

    def list_pages_for_audit(self) -> list[dict]:
        return self._select_all("rag_pages", "url,title,pagerank,embedding,sitemap_present")

    def list_links(self) -> list[dict]:
        return self._select_all("rag_links", "source_url,target_url,anchor_text,is_internal")

    def mark_missing_from_sitemap(self, urls: list[str]) -> None:
        missing_at = datetime.now(timezone.utc).isoformat()
        for url in urls:
            self.client.table("rag_pages").update({
                "sitemap_present": False,
                "missing_from_sitemap_at": missing_at,
            }).eq("url", url).execute()

    def update_pagerank(self, scores: dict[str, float]) -> None:
        for url, score in scores.items():
            self.client.table("rag_pages").update({"pagerank": score}).eq("url", url).execute()

    def match_pages(self, embedding: list[float], match_count: int = 10) -> list[dict]:
        result = self.client.rpc(
            "match_rag_pages",
            {"query_embedding": embedding, "match_count": match_count},
        ).execute()
        return result.data or []

    def match_chunks(self, embedding: list[float], match_count: int = 20) -> list[dict]:
        result = self.client.rpc(
            "match_rag_chunks",
            {"query_embedding": embedding, "match_count": match_count},
        ).execute()
        return result.data or []


def parse_embedding(value: object) -> list[float] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [float(item) for item in value]
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("["):
            return [float(item) for item in ast.literal_eval(text)]
    return None
