create table if not exists rag_pages (
  id bigserial primary key,
  url text not null unique,
  canonical_url text,
  title text,
  description text,
  content text,
  content_hash text,
  embedding vector(1536),
  status_code int,
  sitemap_present boolean default true,
  last_seen_in_sitemap_at timestamptz,
  missing_from_sitemap_at timestamptz,
  last_crawled_at timestamptz,
  last_changed_at timestamptz,
  pagerank double precision default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists rag_chunks (
  id bigserial primary key,
  page_id bigint references rag_pages(id) on delete cascade,
  url text not null,
  chunk_index int not null,
  content text not null,
  content_hash text not null,
  embedding vector(1536),
  token_estimate int,
  created_at timestamptz default now(),
  unique(url, chunk_index)
);

create table if not exists rag_links (
  id bigserial primary key,
  source_url text not null,
  target_url text not null,
  anchor_text text,
  rel text,
  is_internal boolean default true,
  created_at timestamptz default now()
);

create table if not exists rag_refresh_runs (
  id uuid primary key default gen_random_uuid(),
  started_at timestamptz default now(),
  finished_at timestamptz,
  sitemap_url_count int default 0,
  processed_count int default 0,
  new_count int default 0,
  changed_count int default 0,
  unchanged_count int default 0,
  failed_count int default 0,
  missing_count int default 0,
  deleted_count int default 0,
  report jsonb default '{}'::jsonb
);

create index if not exists idx_rag_pages_url on rag_pages(url);
create index if not exists idx_rag_pages_sitemap_present on rag_pages(sitemap_present);
create index if not exists idx_rag_chunks_url on rag_chunks(url);
create index if not exists idx_rag_links_source on rag_links(source_url);
create index if not exists idx_rag_links_target on rag_links(target_url);
create index if not exists idx_rag_pages_embedding on rag_pages using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index if not exists idx_rag_chunks_embedding on rag_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);
