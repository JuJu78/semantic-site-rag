from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse

import requests
import trafilatura
from bs4 import BeautifulSoup

from .config import Settings
from .hashing import normalize_space
from .urls import absolute_url, normalize_url, same_site


@dataclass
class CrawledPage:
    url: str
    final_url: str
    status_code: int
    title: str | None
    description: str | None
    content: str
    links: list[dict]


class SiteCrawler:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

    def fetch_sitemap_urls(self, sitemap_url: str) -> list[str]:
        response = self.session.get(sitemap_url, timeout=self.settings.request_timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "xml")
        urls = [normalize_url(loc.get_text(strip=True)) for loc in soup.find_all("loc")]
        xml_urls = [url for url in urls if url.lower().endswith(".xml")]
        page_urls = [url for url in urls if not url.lower().endswith(".xml")]
        for nested in xml_urls:
            page_urls.extend(self.fetch_sitemap_urls(nested))
        return sorted(set(page_urls))

    def fetch_many_sitemaps(self, sitemap_urls: Iterable[str]) -> list[str]:
        found: set[str] = set()
        for sitemap_url in sitemap_urls:
            found.update(self.fetch_sitemap_urls(sitemap_url))
        return sorted(found)

    def crawl(self, url: str) -> CrawledPage:
        response = self.session.get(url, timeout=self.settings.request_timeout, allow_redirects=True)
        status_code = response.status_code
        final_url = normalize_url(response.url)
        html = response.text if "text/html" in response.headers.get("content-type", "") else ""
        soup = BeautifulSoup(html, "html.parser")
        title = normalize_space(soup.title.get_text(" ")) if soup.title else None
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = normalize_space(description_tag.get("content")) if description_tag else None
        content = trafilatura.extract(html, url=final_url, include_comments=False, include_tables=True) or ""
        content = normalize_space(content)
        base = self.settings.site_base_url or f"{urlparse(final_url).scheme}://{urlparse(final_url).netloc}"
        links = []
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href")
            if not href or href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            target = absolute_url(href, final_url)
            links.append({
                "source_url": final_url,
                "target_url": target,
                "anchor_text": normalize_space(anchor.get_text(" "))[:500],
                "rel": " ".join(anchor.get("rel", [])) if anchor.get("rel") else None,
                "is_internal": same_site(target, base),
            })
        return CrawledPage(
            url=normalize_url(url),
            final_url=final_url,
            status_code=status_code,
            title=title,
            description=description,
            content=content,
            links=links,
        )
