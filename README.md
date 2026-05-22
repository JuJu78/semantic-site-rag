# Semantic Site RAG

Build a living semantic knowledge base for any website with Supabase, pgvector, OpenAI embeddings, internal links, anchors, PageRank, and incremental daily refreshes.

This project is designed for SEO practitioners, content teams, and technical beginners who want to connect Supabase to ChatGPT or Codex and ask useful questions about their own site:

- Which pages have too few internal links?
- Which anchors point to a URL?
- Which pages are semantically close and should link to each other?
- Which pages are far from the site centroid?
- Which sitemap URLs changed since the last crawl?
- Which deleted or redirected URLs should be cleaned from the RAG database?

## What It Does

- Discovers URLs from one or more sitemap XML files, or from a manual URL list.
- Extracts readable page content.
- Splits pages into chunks.
- Creates OpenAI embeddings for pages and chunks.
- Stores pages, chunks, internal links, anchors, refresh runs, and PageRank scores in Supabase.
- Re-embeds only when page content changed.
- Marks and optionally deletes URLs no longer present in the sitemap.
- Produces daily refresh reports.

## Quick Start

Full French beginner tutorial: `docs/tutorial-fr.md`.

```bash
git clone https://github.com/JuJu78/semantic-site-rag.git
cd semantic-site-rag
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Then:

1. Create a Supabase project.
2. Run the SQL files in `sql/` from the Supabase SQL editor, in numerical order. `004_enable_rls.sql` enables Row Level Security on every RAG table and is **mandatory** (see [Security](#security)).
3. Fill `.env` with your Supabase and OpenAI keys.
4. Run your first crawl:

```bash
python scripts/ingest_site.py --sitemap https://example.com/sitemap.xml
```

You can also store one newly published URL:

```bash
python scripts/ingest_site.py --url https://example.com/new-page
```

5. Compute PageRank:

```bash
python scripts/compute_pagerank.py
```

6. Refresh incrementally later:

```bash
python scripts/refresh_daily.py --sitemap https://example.com/sitemap.xml
```

7. Find internal-link opportunities from a draft without storing it:

```bash
python scripts/find_link_opportunities.py --text-file draft.md
```

This creates a temporary embedding for the draft, searches stored Supabase pages and chunks, and writes `reports/link_opportunities.json`. The draft content and embedding are not inserted into Supabase.

## Connect To ChatGPT Or Codex

Once the data is in Supabase, connect the native Supabase connector to ChatGPT or Codex and ask questions directly against your tables. See `docs/connect_chatgpt_codex.md`.

## Cost Control

The refresh script stores a content hash for every page. If a URL has not changed since the last crawl, it is not re-embedded. This avoids paying every day to embed the same website again.

## Security

Supabase exposes every table created in the `public` schema through its PostgREST API. By default the `anon` API key — the one you would naturally paste into a frontend, a notebook, or a third-party tool — can read **and write** the RAG tables. That means anyone who gets hold of that key can scrape your entire crawl, inject fake links, or wipe rows.

This repository ships `sql/004_enable_rls.sql`, which turns on Row Level Security on all RAG tables without attaching any policy. The ingestion and refresh scripts connect with the `service_role` key (which bypasses RLS), so the crawler keeps working, while `anon` and `authenticated` requests are denied by default.

Two rules to keep this safe over time:

- **Never commit your `service_role` key.** It has full write access to your database. Treat it like a root password.
- If you later expose this data publicly (a dashboard, a chatbot, an embedding-search demo), add explicit `create policy` statements granting `select` only — never `insert`, `update`, or `delete` to the `anon` role.

Reference: [Supabase Row Level Security documentation](https://supabase.com/docs/guides/database/postgres/row-level-security).

## License

MIT
