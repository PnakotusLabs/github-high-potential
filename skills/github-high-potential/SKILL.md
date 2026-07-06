---
name: github-high-potential
description: "Generate an AI high-potential GitHub project half-day report from this project’s local scripts and publish Top items for the last 12 hours. Use for requests like: 半日报, 高潜力, AI高潜项目, github-high-potential, halfday."
license: Proprietary. LICENSE.txt has complete terms
---

# AI 高潜力项目半日报（12 小时）

## Overview

Run `./scripts/run_halfday.sh` in the project and summarize:

- generated report path
- number of candidates
- Top 5 entries

This skill is for quick daily intelligence on high-potential GitHub projects.

## Procedure

### 1) Run

```bash
cd /path/to/github-high-potential
./scripts/run_halfday.sh
```

### 2) Read report

The script writes one markdown file under `reports/halfday/`.

### 3) Output summary

- 报告路径
- 候选数量
- Top 5 条目（按分数）

