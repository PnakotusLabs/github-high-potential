from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..config import PRODUCTHUNT_TOKEN
from ..http import client
from ..models import Item


QUERY = """
query Posts($postedAfter: DateTime!) {
  posts(postedAfter: $postedAfter, first: 30) {
    edges {
      node {
        id
        name
        tagline
        url
        votesCount
        commentsCount
        createdAt
        topics { edges { node { name } } }
      }
    }
  }
}
"""


def collect(hours: int = 12) -> list[Item]:
    if not PRODUCTHUNT_TOKEN:
        return []
    posted_after = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with client({"Authorization": f"Bearer {PRODUCTHUNT_TOKEN}"}) as c:
        resp = c.post(
            "https://api.producthunt.com/v2/api/graphql",
            json={"query": QUERY, "variables": {"postedAfter": posted_after}},
        )
        resp.raise_for_status()
        data = resp.json()
    items: list[Item] = []
    for edge in data.get("data", {}).get("posts", {}).get("edges", []):
        node = edge["node"]
        tags = [
            topic["node"]["name"]
            for topic in node.get("topics", {}).get("edges", [])
            if topic.get("node", {}).get("name")
        ]
        items.append(
            Item(
                source="producthunt",
                external_id=node["id"],
                title=node["name"],
                url=node["url"],
                summary=node.get("tagline") or "",
                published_at=datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00")),
                tags=tags,
                metrics={"votes": node.get("votesCount", 0), "comments": node.get("commentsCount", 0)},
            )
        )
    return items
