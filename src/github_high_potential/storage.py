from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Item


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        create table if not exists items (
          stable_key text primary key,
          source text not null,
          external_id text not null,
          title text not null,
          url text not null,
          summary text,
          published_at text not null,
          authors_json text not null,
          tags_json text not null,
          metrics_json text not null,
          first_seen_at text not null,
          last_seen_at text not null
        )
        """
    )
    return conn


def upsert_items(conn: sqlite3.Connection, items: list[Item]) -> int:
    now = datetime.now(timezone.utc).isoformat()
    changed = 0
    for item in items:
        conn.execute(
            """
            insert into items (
              stable_key, source, external_id, title, url, summary, published_at,
              authors_json, tags_json, metrics_json, first_seen_at, last_seen_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            on conflict(stable_key) do update set
              title=excluded.title,
              url=excluded.url,
              summary=excluded.summary,
              published_at=excluded.published_at,
              authors_json=excluded.authors_json,
              tags_json=excluded.tags_json,
              metrics_json=excluded.metrics_json,
              last_seen_at=excluded.last_seen_at
            """,
            (
                item.stable_key,
                item.source,
                item.external_id,
                item.title,
                str(item.url),
                item.summary,
                item.published_at.isoformat(),
                json.dumps(item.authors, ensure_ascii=False),
                json.dumps(item.tags, ensure_ascii=False),
                json.dumps(item.metrics, ensure_ascii=False),
                now,
                now,
            ),
        )
        changed += 1
    conn.commit()
    return changed


def load_recent(conn: sqlite3.Connection, since: datetime) -> list[Item]:
    rows = conn.execute(
        """
        select * from items
        where published_at >= ? or first_seen_at >= ? or last_seen_at >= ?
        order by published_at desc
        """,
        (since.isoformat(), since.isoformat(), since.isoformat()),
    ).fetchall()
    return [
        Item(
            source=row["source"],
            external_id=row["external_id"],
            title=row["title"],
            url=row["url"],
            summary=row["summary"] or "",
            published_at=datetime.fromisoformat(row["published_at"]),
            authors=json.loads(row["authors_json"]),
            tags=json.loads(row["tags_json"]),
            metrics=json.loads(row["metrics_json"]),
        )
        for row in rows
    ]
