from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class Item(BaseModel):
    source: str
    external_id: str
    title: str
    url: HttpUrl | str
    summary: str = ""
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    authors: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)

    @property
    def stable_key(self) -> str:
        return f"{self.source}:{self.external_id}"


class ScoredItem(BaseModel):
    item: Item
    score: float
    reasons: list[str]
