from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from semantic_site_rag.config import get_settings
from semantic_site_rag.database import RagDatabase, parse_embedding


def cosine_distance(vector: np.ndarray, centroid: np.ndarray) -> float:
    denominator = float(np.linalg.norm(vector) * np.linalg.norm(centroid))
    if denominator == 0:
        return 1.0
    return 1.0 - float(np.dot(vector, centroid) / denominator)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit internal links and semantic outliers from Supabase RAG tables.")
    parser.add_argument("--min-incoming", type=int, default=3)
    parser.add_argument("--top", type=int, default=25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    db = RagDatabase(settings)
    pages = db.list_pages_for_audit()
    links = [link for link in db.list_links() if link.get("is_internal")]

    incoming = Counter(link["target_url"] for link in links)
    outgoing = Counter(link["source_url"] for link in links)
    anchors_by_target: dict[str, list[str]] = defaultdict(list)
    for link in links:
        if link.get("anchor_text"):
            anchors_by_target[link["target_url"]].append(link["anchor_text"])

    embedded_pages = []
    for page in pages:
        embedding = parse_embedding(page.get("embedding"))
        if embedding:
            embedded_pages.append((page, np.array(embedding, dtype=float)))

    centroid = np.mean([vector for _page, vector in embedded_pages], axis=0) if embedded_pages else None
    semantic_outliers = []
    if centroid is not None:
        for page, vector in embedded_pages:
            semantic_outliers.append({
                "url": page["url"],
                "title": page.get("title"),
                "centroid_distance": cosine_distance(vector, centroid),
                "incoming_links": incoming[page["url"]],
                "outgoing_links": outgoing[page["url"]],
                "pagerank": page.get("pagerank"),
            })

    low_incoming = [
        {
            "url": page["url"],
            "title": page.get("title"),
            "incoming_links": incoming[page["url"]],
            "outgoing_links": outgoing[page["url"]],
            "pagerank": page.get("pagerank"),
            "sample_anchors": anchors_by_target[page["url"]][:10],
        }
        for page in pages
        if incoming[page["url"]] < args.min_incoming
    ]

    report = {
        "page_count": len(pages),
        "link_count": len(links),
        "low_incoming_pages": sorted(low_incoming, key=lambda item: item["incoming_links"])[: args.top],
        "semantic_outliers": sorted(semantic_outliers, key=lambda item: item["centroid_distance"], reverse=True)[: args.top],
    }

    Path("reports").mkdir(exist_ok=True)
    Path("reports/site_audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
