from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 180) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)
