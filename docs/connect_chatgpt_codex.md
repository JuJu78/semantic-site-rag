# Connect Supabase To ChatGPT Or Codex

After your tables are filled, connect the native Supabase connector in ChatGPT or Codex.

## Useful Tables

- `rag_pages`: one row per URL.
- `rag_chunks`: one row per semantic chunk.
- `rag_links`: one row per discovered internal link.
- `rag_refresh_runs`: one row per crawl or refresh.

## Example Questions

- Find pages with fewer than 3 internal backlinks.
- Which anchors point to `/my-page/`?
- Which chunks are closest to this topic: `enterprise SEO reporting`?
- Which pages are semantically farthest from the site centroid?
- Which URLs disappeared from the sitemap during the last refresh?
- Suggest 20 internal links I should add between related pages.
