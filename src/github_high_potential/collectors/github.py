from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup

from ..config import GITHUB_TOKEN
from ..http import client
from ..models import Item


def collect(hours: int = 12) -> list[Item]:
    return _collect_search(hours) + _collect_trending()


def _collect_search(hours: int) -> list[Item]:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours * 4)).date().isoformat()
    keywords = ["AI", "LLM", "agent", "RAG", "MCP", "inference", "machine-learning"]
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    repos: dict[int, dict] = {}
    with client(headers) as c:
        for keyword in keywords:
            query = f"{keyword} created:>={since} stars:>10"
            resp = c.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "sort": "stars", "order": "desc", "per_page": 20},
            )
            resp.raise_for_status()
            for repo in resp.json().get("items", []):
                repos[repo["id"]] = repo
    items: list[Item] = []
    for repo in repos.values():
        published = _parse_dt(repo.get("created_at")) or datetime.now(timezone.utc)
        topics = repo.get("topics") or []
        desc = repo.get("description") or ""
        items.append(
            Item(
                source="github",
                external_id=str(repo["id"]),
                title=repo["full_name"],
                url=repo["html_url"],
                summary=desc,
                published_at=published,
                authors=[repo["owner"]["login"]],
                tags=topics,
                metrics={
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "open_issues": repo.get("open_issues_count", 0),
                    "language": repo.get("language"),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                },
            )
        )
    return items


def _collect_trending() -> list[Item]:
    with client({"Accept": "text/html"}) as c:
        resp = c.get("https://github.com/trending", params={"since": "daily"})
        resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items: list[Item] = []
    for article in soup.select("article.Box-row")[:25]:
        title_node = article.select_one("h2 a")
        if not title_node:
            continue
        repo_path = " ".join(title_node.get_text(" ", strip=True).split()).replace(" / ", "/")
        desc_node = article.select_one("p")
        lang_node = article.select_one("[itemprop='programmingLanguage']")
        stars_node = article.select_one("a[href$='/stargazers']")
        external_id = repo_path.lower()
        items.append(
            Item(
                source="github_trending",
                external_id=external_id,
                title=repo_path,
                url=f"https://github.com/{repo_path}",
                summary=desc_node.get_text(" ", strip=True) if desc_node else "",
                published_at=datetime.now(timezone.utc),
                tags=[lang_node.get_text(strip=True)] if lang_node else [],
                metrics={"stars_text": stars_node.get_text(strip=True) if stars_node else ""},
            )
        )
    return items


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
