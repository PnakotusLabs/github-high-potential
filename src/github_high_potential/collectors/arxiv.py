from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from ..http import client
from ..models import Item


NS = {"atom": "http://www.w3.org/2005/Atom"}


def collect(hours: int = 12) -> list[Item]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours * 2)
    query = "cat:cs.AI OR cat:cs.CL OR cat:cs.LG OR cat:cs.CV"
    with client({"Accept": "application/atom+xml"}) as c:
        resp = c.get(
            "https://export.arxiv.org/api/query",
            params={
                "search_query": query,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "start": 0,
                "max_results": 50,
            },
        )
        resp.raise_for_status()
    root = ET.fromstring(resp.text)
    items: list[Item] = []
    for entry in root.findall("atom:entry", NS):
        published = _text(entry, "atom:published")
        published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
        if published_at < cutoff:
            continue
        url = _text(entry, "atom:id")
        title = " ".join(_text(entry, "atom:title").split())
        summary = " ".join(_text(entry, "atom:summary").split())
        authors = [
            _text(author, "atom:name")
            for author in entry.findall("atom:author", NS)
            if _text(author, "atom:name")
        ]
        tags = [
            cat.attrib.get("term", "")
            for cat in entry.findall("atom:category", NS)
            if cat.attrib.get("term")
        ]
        items.append(
            Item(
                source="arxiv",
                external_id=url.rsplit("/", 1)[-1],
                title=title,
                url=url,
                summary=summary[:700],
                published_at=published_at,
                authors=authors[:5],
                tags=tags,
                metrics={"authors_count": len(authors)},
            )
        )
    return items


def _text(node: ET.Element, path: str) -> str:
    child = node.find(path, NS)
    return child.text.strip() if child is not None and child.text else ""
