from __future__ import annotations

from urllib.parse import urldefrag, urljoin, urlparse


def normalize_url(url: str) -> str:
    clean, _fragment = urldefrag(url.strip())
    parsed = urlparse(clean)
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return parsed._replace(path=path, query=parsed.query).geturl()


def same_site(url: str, base_url: str) -> bool:
    return urlparse(url).netloc.lower() == urlparse(base_url).netloc.lower()


def absolute_url(href: str, source_url: str) -> str:
    return normalize_url(urljoin(source_url, href))
