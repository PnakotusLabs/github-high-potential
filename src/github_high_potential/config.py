from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "github-high-potential.sqlite3"
REPORT_DIR = ROOT / "reports" / "halfday"

load_dotenv(ROOT / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
PRODUCTHUNT_TOKEN = os.getenv("PRODUCTHUNT_TOKEN", "")

AI_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "llm",
    "large language model",
    "agent",
    "agents",
    "rag",
    "retrieval",
    "mcp",
    "model context protocol",
    "inference",
    "eval",
    "evaluation",
    "multimodal",
    "text-to-image",
    "text to image",
    "voice ai",
    "coding agent",
    "copilot",
    "workflow automation",
]

HIGH_VALUE_KEYWORDS = [
    "agent",
    "coding agent",
    "mcp",
    "rag",
    "inference",
    "eval",
    "multimodal",
    "local",
    "open source",
    "developer tool",
    "workflow",
    "automation",
    "benchmark",
]

# RSS feed groups: one for official vendor pages, one for secondary aggregation/commentary sources
RSS_PRIMARY_FEEDS = {
    "openai": "https://openai.com/news/rss.xml",
    "anthropic": "https://www.anthropic.com/news/rss.xml",
    "huggingface": "https://huggingface.co/blog/feed.xml",
}

RSS_SECONDARY_FEEDS = {
    "techcrunch_ai": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "venturebeat_ai": "https://venturebeat.com/category/ai/feed/",
    "techmeme": "https://www.techmeme.com/feed.xml",
    "aitrends": "https://www.aitrends.com/feed/",
    "ai_news": "https://www.artificialintelligence-news.com/feed/",
    "synced": "https://syncedreview.com/feed/",
    "mlmastery": "https://machinelearningmastery.com/feed/",
    "hn_frontpage": "https://hnrss.org/frontpage",
    "lobsters": "https://lobste.rs/rss",
    "zdnet_ai": "https://www.zdnet.com/news/rss.xml",
}
