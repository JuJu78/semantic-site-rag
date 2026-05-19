from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_embedding_model: str
    supabase_url: str
    supabase_service_role_key: str
    site_base_url: str | None
    chunk_size: int
    chunk_overlap: int
    request_timeout: int
    crawl_delay_seconds: float
    user_agent: str


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing {name}. Copy .env.example to .env and fill this value.")
    return value


def get_settings() -> Settings:
    return Settings(
        openai_api_key=require_env("OPENAI_API_KEY"),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        supabase_url=require_env("SUPABASE_URL"),
        supabase_service_role_key=require_env("SUPABASE_SERVICE_ROLE_KEY"),
        site_base_url=os.getenv("SITE_BASE_URL"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "1200")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "180")),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        crawl_delay_seconds=float(os.getenv("CRAWL_DELAY_SECONDS", "1.0")),
        user_agent=os.getenv("USER_AGENT", "SemanticSiteRAG/0.1"),
    )
