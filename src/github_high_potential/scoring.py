from __future__ import annotations

import math
import re
from datetime import datetime, timezone

from .config import AI_KEYWORDS, HIGH_VALUE_KEYWORDS
from .models import Item, ScoredItem


def score_items(items: list[Item]) -> list[ScoredItem]:
    scored = [score_item(item) for item in items]
    return sorted(scored, key=lambda row: row.score, reverse=True)


def score_item(item: Item) -> ScoredItem:
    now = datetime.now(timezone.utc)
    age_hours = max((now - item.published_at).total_seconds() / 3600, 0)
    freshness = max(0, 25 - age_hours) / 25 * 20
    tag_text = "" if item.source == "hackernews" else " ".join(item.tags)
    text = f"{item.title} {item.summary} {tag_text}".lower()
    relevance_hits = [kw for kw in AI_KEYWORDS if _has_keyword(text, kw)]
    high_value_hits = [kw for kw in HIGH_VALUE_KEYWORDS if _has_keyword(text, kw)]
    relevance = min(25, len(relevance_hits) * 5 + len(high_value_hits) * 4)
    velocity, velocity_reason = _velocity(item)
    discussion = min(15, math.log1p(_metric(item, "comments")) * 4)
    novelty = 10 if high_value_hits else 4
    score = round(freshness + relevance + velocity + discussion + novelty, 1)

    reasons = []
    if relevance_hits:
        reasons.append(f"AI relevance: {', '.join(relevance_hits[:5])}")
    if high_value_hits:
        reasons.append(f"High-value tags: {', '.join(high_value_hits[:4])}")
    if velocity_reason:
        reasons.append(velocity_reason)
    if _metric(item, "comments"):
        reasons.append(f"Discussion: {_metric(item, 'comments')} comments")
    reasons.append(f"Freshness: {age_hours:.1f}h old")
    return ScoredItem(item=item, score=min(score, 100), reasons=reasons)


def _velocity(item: Item) -> tuple[float, str]:
    stars = _metric(item, "stars")
    forks = _metric(item, "forks")
    points = _metric(item, "points")
    votes = _metric(item, "votes")
    if stars:
        return min(30, math.log1p(stars) * 5 + math.log1p(forks) * 3), f"GitHub traction: {stars} stars, {forks} forks"
    if points:
        return min(30, math.log1p(points) * 6), f"HN traction: {points} points"
    if votes:
        return min(30, math.log1p(votes) * 5), f"Product Hunt traction: {votes} votes"
    if item.source.startswith("rss"):
        return 8, "News/source signal"
    if item.source == "arxiv":
        return 6, "Research signal"
    return 3, ""


def _metric(item: Item, key: str) -> int:
    value = item.metrics.get(key) or 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _has_keyword(text: str, keyword: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(keyword.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None
