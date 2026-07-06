from . import arxiv, github, hackernews, producthunt, rss

COLLECTORS = {
    "github": github.collect,
    "hackernews": hackernews.collect,
    "arxiv": arxiv.collect,
    "rss": rss.collect,
    "producthunt": producthunt.collect,
}
