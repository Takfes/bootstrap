---
name: search-web
version: 1.2
description: Perform web searches using SerpAPI with customizable filters for site, date range, and language. Use when users request web searches with natural language queries like "find articles about [topic]", "search GitHub for [query] from 2026", "news on [subject] from the past week", or "site:domain.com [search term]". Returns structured, token-efficient results in markdown table format with titles, URLs, publication dates, and snippets.
---

# Web Search

## Overview

Search the internet efficiently using SerpAPI Google Light Search. Supports general web searches, site-specific searches (e.g., GitHub), and time-filtered queries. Returns results in a compact markdown table with titles, URLs, dates, and snippets.

## Quick Start

Basic usage with all defaults (past month, 20 results, any domain):

```
User: "Search for claude-skills repositories from 2026"

Output:
**Google Search: "claude-skills"** | 20 results | From 2026 | GitHub (site:github.com)

| # | Title | URL | Date | Snippet |
|---|---|---|---|---|
| 1 | ComposioHQ/awesome-claude-skills - GitHub | [Link](https://github.com/ComposioHQ/awesome-claude-skills) | Feb 3, 2026 | Claude Skills are customizable workflows... |
| 2 | trailofbits/skills: Trail of Bits Claude Code... | [Link](https://github.com/trailofbits/skills) | Jan 17, 2026 | A Claude Code plugin marketplace... |
```

## Customizable Parameters

Users can override defaults inline in their request:

| Parameter | Default | Override Examples |
|-----------|---------|-------------------|
| Search Query | Required | Any natural language search term |
| Site Filter | None | "site:github.com", "site:medium.com", "site:news.ycombinator.com" |
| Time Period | Past month | "past week", "past 24 hours", "past year", "from 2026" |
| limit | 20 | "show 5 results", "top 50 results" |
| Output Format | Markdown table | "as a list", "JSON format", "CSV" |

## Token Optimization Rules

1. **No preamble** - Skip "Sure, here are the results" and similar filler
2. **Single summary line** - One line header above results, not paragraphs
3. **Compact dates** - Format as "Feb 3, 2026" or "Jan 17, 2026"
4. **Truncate titles** - Max 80 characters, append "…" if longer
5. **Truncate snippets** - Max 100 characters, append "…" if longer
6. **Clean URLs** - Show domain only or abbreviated path (e.g., "github.com/user/repo")
7. **Minimal columns** - Only title, URL, date, snippet unless user requests more
8. **No analysis** - Return results only unless explicitly asked for commentary

## Execution Workflow

**IMPORTANT:**
- **Do NOT call `RUBE_SEARCH_TOOLS`** — the tool slugs are pre-determined below
- **Target: 1 Rube call + 0 workbench calls.** No more.

### 1. Parse User Request

Extract:

- **query** (REQUIRED): The search term(s) - ask if missing or ambiguous
- **site** (optional): Domain filter — default: None (all sites)
- **period** (optional): Time filter — default: "past month"
- **limit** (optional): Number of results — default: 20
- **output_format** (optional): Output style — default: "markdown_table"

### 2. Map Time Period to Query Filter

When user specifies a time period, append it to the query in Google search format:

| User Says | Query Append |
|-----------|--------------|
| past 24 hours | `after:<today - 1>` |
| past week | `after:<today - 7>` |
| past month | `after:<today - 30>` |
| past 3 months | `after:<today - 90>` |
| from 2026 | `after:2026-01-01` |
| all time | omit entirely |
| from 2024-12-01 to 2025-01-15 | `after:2024-12-01 before:2025-01-15` |

**Site filter:** If user specifies site (e.g., "GitHub"), prepend `site:github.com` to query.

### 3. Build Query String

Construct the final query combining:
1. Site filter (if provided): `site:github.com`
2. User's search term
3. Time filter (if provided): `after:2026-01-01`

Example: `site:github.com claude-skills after:2026-01-01`

### 4. Execute Search

Call `mcp__rube__RUBE_MULTI_EXECUTE_TOOL` with these exact parameters:

- `tools`: `[{"tool_slug": "SERPAPI_GOOGLE_LIGHT_SEARCH", "arguments": {"q": "<final_query>", "num": 20}}]`
- `sync_response_to_workbench`: `false` (inline processing only)
- `memory`: `{}` **(REQUIRED — always include, even if empty)**
- `current_step`: `"SEARCH"`
- `thought`: `"Searching internet for <query>"`

**Do NOT pass `session` or `session_id`.** This is a stateless search.

**Response structure:**
```
organic_results[].title         → Result title
organic_results[].link          → Full URL
organic_results[].date          → Publication date
organic_results[].snippet       → Result snippet/description
```

### 5. Format Output

Process results directly inline. Sort by relevance (API order).

**Default format:** Markdown table with summary header line.

**Alternative formats (if requested):**
- **list**: `1. **Title** — [Link](url) — Date — Snippet`
- **JSON**: Raw array of objects
- **CSV**: Comma-separated with headers

## Token Optimization Checklist

- [ ] No `RUBE_SEARCH_TOOLS` call (tools are pre-determined)
- [ ] `memory: {}` included in `RUBE_MULTI_EXECUTE_TOOL` call
- [ ] No `session` or `session_id` (stateless search)
- [ ] No preamble text ("I found...", "Here are...")
- [ ] No post-table analysis unless requested
- [ ] Single summary line above results
- [ ] Compact date formatting ("Feb 3, 2026")
- [ ] Truncated titles (80 char max)
- [ ] Truncated snippets (100 char max)
- [ ] URL as `[Link](url)` not raw URL
- [ ] No unnecessary columns
- [ ] Results in order returned (no custom sorting unless requested)

## Edge Cases

| Scenario | Response |
|----------|----------|
| No query | Ask user for search term |
| No results | "No results found for '[query]'. Try broadening your search or removing date filters." |
| Fewer results than requested | Show available results (no note needed) |
| MCP error | "Search failed. Check that SerpAPI connection is active." |

## Common User Requests

| User Request | How to Handle |
|---|---|
| "Search for [term]" | Standard search, default parameters |
| "Search GitHub for [term]" | Prepend `site:github.com` to query |
| "Search from [period]" | Map period to date filter, append to query |
| "Show me 5 results" | Parse limit = 5 |
| "Include channel/author info" | Add extra column if available |
| "As a JSON list" | Output in JSON format |
| "site:example.com [query]" | Extract site from query, pass as-is |
| "From 2026" | Append `after:2026-01-01` to query |

## References

See `references/api_reference.md` for detailed technical specifications and SerpAPI response structure documentation.

## Related Skills

**Other search skills:** `/search-youtube` · `/search-zotero` · `/search-perplexity`
