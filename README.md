# GitHub High Potential

Codex skill and local workflow for generating a 12-hour AI high-potential project report.

The skill entry lives at `skills/github-high-potential/SKILL.md`. When Codex triggers the skill, it runs `scripts/run_halfday.sh`, collects recent AI project signals, scores them, and writes a Markdown report under `reports/halfday/`.

## What It Collects

- GitHub repository search results for AI, LLM, agent, RAG, MCP, inference, and machine learning keywords.
- GitHub daily trending repositories.
- Hacker News stories matching AI-related queries.
- Recent arXiv papers from AI, CL, LG, and CV categories.
- RSS entries from AI vendor blogs and secondary tech/news sources.
- Product Hunt posts when `PRODUCTHUNT_TOKEN` is configured.

## Quick Start

```bash
./scripts/run_halfday.sh
```

The script will:

1. Find a Python 3.11+ interpreter.
2. Create `.venv` if needed.
3. Install this project in editable mode.
4. Run `github-high-potential run`.
5. Write a report to `reports/halfday/YYYY-MM-DD-AM.md` or `reports/halfday/YYYY-MM-DD-PM.md`.

## Configuration

Optional environment variables:

```bash
GITHUB_TOKEN=...
PRODUCTHUNT_TOKEN=...
GITHUB_HIGH_POTENTIAL_HOURS=12
GITHUB_HIGH_POTENTIAL_LIMIT=30
PYTHON_BIN=/path/to/python3.12
```

Legacy variables `TECHNEWS_HOURS` and `TECHNEWS_LIMIT` are still accepted for compatibility.

## CLI

After installation, the CLI is available as:

```bash
github-high-potential run --hours 12 --limit 30
github-high-potential collect --hours 12
github-high-potential report --hours 12 --limit 30
```

## Output

Generated files are intentionally ignored by Git:

- `data/github-high-potential.sqlite3`
- `reports/halfday/*.md`

Each report includes:

- generation time
- observation window
- candidate count
- trend snapshot
- ranked project/signal sections
- source distribution

## Verification

```bash
bash -n scripts/run_halfday.sh
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m compileall -q src tests
```
