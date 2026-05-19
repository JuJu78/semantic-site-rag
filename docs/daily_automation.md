# Daily Automation

The refresh script is incremental. It compares the latest page content hash with the stored hash.

- New URL: crawled, chunked, embedded, and stored.
- Changed URL: old chunks are replaced and embeddings are regenerated.
- Unchanged URL: metadata and links can be refreshed, but embeddings are not regenerated.
- Missing URL: marked as absent from the latest sitemap.

## Run Manually

```bash
python scripts/refresh_daily.py --sitemap https://example.com/sitemap.xml
```

## Windows Task Scheduler

Create a daily task that runs:

```bash
D:\path\to\semantic-site-rag\.venv\Scripts\python.exe D:\path\to\semantic-site-rag\scripts\refresh_daily.py --sitemap https://example.com/sitemap.xml
```

## GitHub Actions

See `.github/workflows/daily-refresh.yml`. Store secrets in GitHub Actions secrets.
