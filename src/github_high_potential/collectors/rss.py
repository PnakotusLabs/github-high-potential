from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser

from ..config import AI_KEYWORDS, RSS_PRIMARY_FEEDS, RSS_SECONDARY_FEEDS
from ..models import Item


FEEDS = {
    **{f"primary:{name}": url for name, url in RSS_PRIMARY_FEEDS.items()},
    **{f"secondary:{name}": url for name, url in RSS_SECONDARY_FEEDS.items()},
}


def collect(hours: int = 12) -> list[Item]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    items: list[Item] = []
    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:20]:
            published_at = _published(entry)
            if published_at < cutoff:
                continue
            title = entry.get("title", "Untitled")
            summary = entry.get("summary", "")
            blob = f"{title} {summary}".lower()
            if not any(keyword in blob for keyword in AI_KEYWORDS):
                continue
            link = entry.get("link", url)
            items.append(
                Item(
                    source=f"rss:{source}",
                    external_id=entry.get("id") or link,
                    title=title,
                    url=link,
                    summary=summary[:600],
                    published_at=published_at,
                    tags=["news", source],
                    metrics={},
                )
            )
    return items


def _published(entry: dict) -> datetime:
    value = entry.get("published") or entry.get("updated")
    if not value:
        return datetime.now(timezone.utc)
    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
