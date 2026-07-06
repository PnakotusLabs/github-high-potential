from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .config import RSS_SECONDARY_FEEDS
from .models import ScoredItem


def write_report(scored: list[ScoredItem], report_dir: Path, hours: int, limit: int) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).astimezone()
    window = "AM" if now.hour < 12 else "PM"
    path = report_dir / f"{now:%Y-%m-%d}-{window}.md"
    buckets = _bucket_by_section(scored)
    section_order = [
        "GitHub 核心项目",
        "GitHub 趋势",
        "Hacker News",
        "Product Hunt",
        "ArXiv",
        "RSS 官方资讯",
        "RSS 二级站点聚合",
        "其他",
    ]
    lines = [
        f"# AI 高潜力项目半日报 - {now:%Y-%m-%d} {window}",
        "",
        f"- 生成时间：{now:%Y-%m-%d %H:%M %Z}",
        f"- 观察窗口：最近 {hours} 小时",
        f"- 入库候选：{len(scored)}",
        "",
        "## 趋势快照",
        "",
    ]
    trends = _trend_lines(scored)
    lines.extend([f"- {line}" for line in trends] or ["- 暂无足够趋势信号。"])
    lines.extend(["", "## Top 项目/信号", ""])
    active_sections = [name for name in section_order if buckets.get(name)]
    section_limit = max(1, limit // max(1, len(active_sections)))
    for section in section_order:
        section_items = buckets.get(section, [])
        if not section_items:
            continue
        lines.extend([f"### {section}", ""])
        cap = min(len(section_items), section_limit)
        for row in section_items[:cap]:
            item = row.item
            lines.extend(
                [
                    f"#### {item.title}",
                    "",
                    f"- 分数：{row.score}",
                    f"- 来源：{item.source}",
                    f"- 链接：{item.url}",
                    f"- 时间：{item.published_at.astimezone():%Y-%m-%d %H:%M %Z}",
                    f"- 摘要：{_clean(item.summary) or '暂无摘要'}",
                    f"- 判断：{'; '.join(row.reasons[:4])}",
                    "",
                ]
            )
    lines.extend(["## 来源分布", ""])
    for source, count in Counter(row.item.source for row in scored).most_common():
        lines.append(f"- {source}: {count}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _trend_lines(scored: list[ScoredItem]) -> list[str]:
    tag_counter: Counter[str] = Counter()
    source_counter: Counter[str] = Counter()
    for row in scored:
        source_counter[row.item.source] += 1
        for tag in row.item.tags:
            normalized = tag.lower().strip()
            if normalized and len(normalized) < 40:
                tag_counter[normalized] += 1
    lines = []
    if tag_counter:
        tags = ", ".join(tag for tag, _ in tag_counter.most_common(8))
        lines.append(f"高频方向：{tags}")
    if source_counter:
        sources = ", ".join(f"{source}({count})" for source, count in source_counter.most_common(5))
        lines.append(f"主要信号源：{sources}")
    return lines


def _clean(value: str) -> str:
    return " ".join(value.replace("\n", " ").split())[:500]


def _bucket_by_section(scored: list[ScoredItem]) -> dict[str, list[ScoredItem]]:
    buckets: defaultdict[str, list[ScoredItem]] = defaultdict(list)
    for row in scored:
        buckets[_section_name(row.item.source)].append(row)
    for bucket in buckets.values():
        bucket.sort(key=lambda row: row.score, reverse=True)
    return buckets


def _section_name(source: str) -> str:
    if source.startswith("github_trending"):
        return "GitHub 趋势"
    if source == "github":
        return "GitHub 核心项目"
    if source == "hackernews":
        return "Hacker News"
    if source == "producthunt":
        return "Product Hunt"
    if source == "arxiv":
        return "ArXiv"
    if source.startswith("rss:"):
        feed = source.rsplit(":", 1)[1]
        kind = source.split(":", 2)[1] if source.count(":") >= 2 else ""
        if kind == "secondary" or feed in RSS_SECONDARY_FEEDS:
            return "RSS 二级站点聚合"
        return "RSS 官方资讯"
    return "其他"
