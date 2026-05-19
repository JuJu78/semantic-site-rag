from __future__ import annotations

from openai import OpenAI

from .config import Settings


class EmbeddingClient:
    def __init__(self, settings: Settings):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model

    def embed(self, text: str) -> list[float]:
        cleaned = text.replace("\n", " ").strip()
        response = self.client.embeddings.create(model=self.model, input=cleaned[:24000])
        return response.data[0].embedding
