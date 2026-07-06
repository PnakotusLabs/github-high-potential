from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..http import client
from ..models import Item


QUERIES = [
    "AI",
    "LLM",
    "agent",
    "RAG",
    "MCP",
    "Show HN AI",
    "open source AI",
]


def collect(hours: int = 12) -> list[Item]:
    cutoff_ts = int((datetime.now(timezone.utc) - timedelta(hours=hours)).timestamp())
    seen: set[str] = set()
    items: list[Item] = []
    with client() as c:
        for query in QUERIES:
            resp = c.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": query,
                    "tags": "story",
                    "numericFilters": f"created_at_i>{cutoff_ts}",
                    "hitsPerPage": 20,
                },
            )
            resp.raise_for_status()
            for hit in resp.json().get("hits", []):
                object_id = hit.get("objectID")
                if not object_id or object_id in seen:
                    continue
                seen.add(object_id)
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
                items.append(
                    Item(
                        source="hackernews",
                        external_id=object_id,
                        title=hit.get("title") or hit.get("story_title") or "Untitled",
                        url=url,
                        summary="",
                        published_at=datetime.fromtimestamp(hit["created_at_i"], tz=timezone.utc),
                        authors=[hit["author"]] if hit.get("author") else [],
                        tags=["hn"],
                        metrics={
                            "points": hit.get("points") or 0,
                            "comments": hit.get("num_comments") or 0,
                            "hn_url": f"https://news.ycombinator.com/item?id={object_id}",
                        },
                    )
                )
    return items
