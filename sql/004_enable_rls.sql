-- Harden default access: enable Row Level Security on all RAG tables.
--
-- Why this matters:
--   Any table created in Supabase's `public` schema is exposed through
--   PostgREST. The anon API key is typically embedded in frontends or
--   shared with third-party tools. Without RLS, anyone holding that key
--   can read AND write rag_pages, rag_chunks, rag_links, etc.
--
-- Why this script is safe:
--   The ingestion and refresh scripts in this repository connect to
--   Supabase with the service_role key, which bypasses Row Level
--   Security. Enabling RLS without attaching any policy denies access
--   to anon and authenticated roles while leaving service_role unaffected.
--
-- If you later expose part of this data to a public dashboard, add
-- explicit read-only policies, e.g.:
--   create policy "read pages anon" on rag_pages for select to anon
--   using (true);
-- Never grant insert/update/delete to the anon role.

alter table rag_pages        enable row level security;
alter table rag_chunks       enable row level security;
alter table rag_links        enable row level security;
alter table rag_refresh_runs enable row level security;
