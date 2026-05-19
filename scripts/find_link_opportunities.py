from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from semantic_site_rag.config import get_settings
from semantic_site_rag.database import RagDatabase
from semantic_site_rag.embeddings import EmbeddingClient
from semantic_site_rag.hashing import normalize_space


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find semantic internal-link opportunities from raw content without storing it."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", help="Raw draft content to compare with stored Supabase pages.")
    input_group.add_argument("--text-file", help="Path to a text or markdown file containing draft content.")
    parser.add_argument("--top-pages", type=int, default=10, help="Number of closest page-level matches.")
    parser.add_argument("--top-chunks", type=int, default=30, help="Number of closest chunk-level matches.")
    parser.add_argument(
        "--output",
        default="reports/link_opportunities.json",
        help="JSON report path. Use '-' to print JSON only.",
    )
    return parser.parse_args()


def read_input(args: argparse.Namespace) -> str:
    if args.text_file:
        return Path(args.text_file).read_text(encoding="utf-8")
    return args.text or ""


def group_chunks_by_url(chunks: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for chunk in chunks:
        url = chunk["url"]
        if url not in grouped:
            grouped[url] = {
                "url": url,
                "best_similarity": chunk.get("similarity", 0),
                "matching_chunks": [],
            }
        grouped[url]["best_similarity"] = max(grouped[url]["best_similarity"], chunk.get("similarity", 0))
        grouped[url]["matching_chunks"].append(
            {
                "chunk_index": chunk.get("chunk_index"),
                "similarity": chunk.get("similarity"),
                "content_preview": normalize_space(chunk.get("content", ""))[:500],
            }
        )
    return sorted(grouped.values(), key=lambda item: item["best_similarity"], reverse=True)


def main() -> None:
    args = parse_args()
    raw_text = normalize_space(read_input(args))
    if not raw_text:
        raise RuntimeError("No input text provided.")

    settings = get_settings()
    db = RagDatabase(settings)
    embedder = EmbeddingClient(settings)

    query_embedding = embedder.embed(raw_text)
    page_matches = db.match_pages(query_embedding, args.top_pages)
    chunk_matches = db.match_chunks(query_embedding, args.top_chunks)
    chunk_matches_by_url = group_chunks_by_url(chunk_matches)

    page_similarity_by_url = {
        match["url"]: match.get("similarity")
        for match in page_matches
    }

    opportunities = []
    for item in chunk_matches_by_url:
        opportunities.append(
            {
                "url": item["url"],
                "page_similarity": page_similarity_by_url.get(item["url"]),
                "best_chunk_similarity": item["best_similarity"],
                "matching_chunks": item["matching_chunks"][:3],
            }
        )

    report = {
        "mode": "temporary_embedding_no_supabase_insert",
        "input_characters": len(raw_text),
        "top_pages": page_matches,
        "link_opportunities": opportunities,
        "note": (
            "The draft embedding was used only for this query. "
            "The raw content and its embedding were not stored in Supabase."
        ),
    }

    output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output == "-":
        print(output)
        return

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    print(f"Wrote {output_path}")
    print(json.dumps(
        {
            "input_characters": report["input_characters"],
            "page_matches": len(page_matches),
            "opportunity_urls": len(opportunities),
            "stored_in_supabase": False,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
