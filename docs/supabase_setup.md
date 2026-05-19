# Beginner Setup Guide

This guide assumes you have never used Supabase before.

## 1. Create A Supabase Project

1. Go to https://supabase.com/
2. Create a free account.
3. Create a new project.
4. Choose a project name and database password.
5. Wait for the project to finish provisioning.

## 2. Find Your API Keys

In Supabase:

1. Open your project.
2. Go to Project Settings > API.
3. Copy the Project URL into `SUPABASE_URL`.
4. Copy the `service_role` key into `SUPABASE_SERVICE_ROLE_KEY`.

Keep the service role key private. Do not publish it on GitHub.

## 3. Run The SQL Setup

Open SQL Editor in Supabase and run these files in order:

1. `sql/001_enable_pgvector.sql`
2. `sql/002_create_tables.sql`
3. `sql/003_create_match_functions.sql`

## 4. Create An OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a key.
3. Add it to `.env` as `OPENAI_API_KEY`.

## 5. Run Your First Ingestion

```bash
python scripts/ingest_site.py --sitemap https://example.com/sitemap.xml
```

For several sitemaps:

```bash
python scripts/ingest_site.py --sitemap https://example.com/sitemap-fr.xml --sitemap https://example.com/sitemap-en.xml
```
