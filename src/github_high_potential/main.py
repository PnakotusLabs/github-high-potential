from __future__ import annotations

from datetime import datetime, timedelta, timezone

import typer

from .collectors import COLLECTORS
from .config import DB_PATH, REPORT_DIR
from .report import write_report
from .scoring import score_items
from .storage import connect, load_recent, upsert_items

app = typer.Typer(no_args_is_help=True)


@app.command()
def collect(
    hours: int = typer.Option(12, help="Collection window in hours."),
    sources: str = typer.Option("github,hackernews,arxiv,rss,producthunt", help="Comma-separated sources."),
) -> None:
    """Collect candidate items into SQLite."""
    selected = [source.strip() for source in sources.split(",") if source.strip()]
    items = []
    for source in selected:
        collector = COLLECTORS.get(source)
        if collector is None:
            typer.echo(f"Skip unknown source: {source}")
            continue
        try:
            batch = collector(hours)
            typer.echo(f"{source}: {len(batch)} items")
            items.extend(batch)
        except Exception as exc:
            typer.echo(f"{source}: failed: {exc}")
    conn = connect(DB_PATH)
    changed = upsert_items(conn, items)
    typer.echo(f"Stored {changed} items in {DB_PATH}")


@app.command()
def report(
    hours: int = typer.Option(12, help="Report window in hours."),
    limit: int = typer.Option(30, help="Maximum items in the report."),
) -> None:
    """Generate a half-day Markdown report from stored items."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    conn = connect(DB_PATH)
    items = load_recent(conn, since)
    scored = score_items(items)
    path = write_report(scored, REPORT_DIR, hours, limit)
    typer.echo(f"Wrote {path}")


@app.command()
def run(
    hours: int = typer.Option(12, help="Collection and report window in hours."),
    limit: int = typer.Option(30, help="Maximum items in the report."),
    sources: str = typer.Option("github,hackernews,arxiv,rss,producthunt", help="Comma-separated sources."),
) -> None:
    """Collect data and generate a half-day report."""
    collect(hours=hours, sources=sources)
    report(hours=hours, limit=limit)


if __name__ == "__main__":
    app()
