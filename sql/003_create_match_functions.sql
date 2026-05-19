create or replace function match_rag_chunks(
  query_embedding vector(1536),
  match_count int default 10
)
returns table (
  id bigint,
  url text,
  chunk_index int,
  content text,
  similarity double precision
)
language sql stable
as $$
  select
    rag_chunks.id,
    rag_chunks.url,
    rag_chunks.chunk_index,
    rag_chunks.content,
    1 - (rag_chunks.embedding <=> query_embedding) as similarity
  from rag_chunks
  where rag_chunks.embedding is not null
  order by rag_chunks.embedding <=> query_embedding
  limit match_count;
$$;

create or replace function match_rag_pages(
  query_embedding vector(1536),
  match_count int default 10
)
returns table (
  id bigint,
  url text,
  title text,
  similarity double precision
)
language sql stable
as $$
  select
    rag_pages.id,
    rag_pages.url,
    rag_pages.title,
    1 - (rag_pages.embedding <=> query_embedding) as similarity
  from rag_pages
  where rag_pages.embedding is not null
  order by rag_pages.embedding <=> query_embedding
  limit match_count;
$$;
