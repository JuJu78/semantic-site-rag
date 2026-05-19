# SEO Use Cases

## 1. Pages With Too Few Internal Links

Run:

```bash
python scripts/audit_site.py --min-incoming 3
```

Then ask ChatGPT or Codex to inspect `rag_pages`, `rag_links`, and `rag_chunks` to suggest source pages that should link to those underlinked URLs.

## 2. Anchor Diversity

Query `rag_links` grouped by `target_url` and `anchor_text`. Repeated exact-match anchors can look unnatural. Very vague anchors like "click here" or "read more" are weak for SEO.

## 3. Semantic Outliers

`audit_site.py` computes each page distance from the site centroid. A high distance can mean:

- The page is outside the core topical cluster.
- The page is thin or poorly extracted.
- The site has several disconnected content silos.

## 4. Link Opportunities

Use vector search on `rag_chunks` to find chunks close to a target page topic. Then check whether those source URLs already link to the target URL. If not, they are internal link candidates.

## 5. Sitemap Cleanup

`refresh_daily.py` marks pages missing from the latest sitemap. This helps detect deleted, redirected, or noindexed pages that should not stay in your RAG base forever.
