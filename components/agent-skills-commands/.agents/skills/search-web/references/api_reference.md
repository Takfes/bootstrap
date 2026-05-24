# Internet Search — Detailed Execution Guide

## Pre-Determined Tool

**Do NOT call `RUBE_SEARCH_TOOLS`.** The required tool is fixed:

| Tool Slug | Purpose | Quota |
|---|---|---|
| `SERPAPI_GOOGLE_LIGHT_SEARCH` | Google search with filters | Rate limited by SerpAPI plan |

Called via `mcp__rube__RUBE_MULTI_EXECUTE_TOOL`.

## SerpAPI Connection

SerpAPI must be connected and active. The connection should be pre-configured with your API key. If auth fails, the response will indicate connection status.

## Step-by-Step Execution

### Step 1: Parse User Request

Extract these parameters from the user's message:

- **query** (REQUIRED): The search term(s)
  - Examples: "claude-skills", "AI agents", "Python tutorials"
  - If missing or ambiguous, ASK the user before proceeding

- **site** (optional): Site filter
  - Examples: "github.com", "medium.com", "news.ycombinator.com"
  - User may say: "Search GitHub for...", "site:domain.com ...", "on GitHub"
  - If mentioned, prepend `site:<domain>` to final query

- **period** (optional): Time filter
  - Default: "past month"
  - User examples: "past 24 hours", "past week", "from 2026", "from 2024"
  - Do NOT apply if user says "all time" or "no time limit"

- **limit** (optional): Number of results
  - Default: 20
  - SerpAPI caps at 100 per request

- **output_format** (optional): Output style
  - Default: "markdown_table"
  - Alternatives: "list", "JSON", "CSV"

### Step 2: Construct Query String

Build the final Google search query:

```
[site_filter] [search_term] [time_filter]
```

**Site filter:** If user specifies site, prepend: `site:github.com`

**Time filter:** Map user period to Google date syntax:

```
Past 24 hours: after:YYYY-MM-DD (today - 1 day)
Past week:     after:YYYY-MM-DD (today - 7 days)
Past month:    after:YYYY-MM-DD (today - 30 days)
Past 3 months: after:YYYY-MM-DD (today - 90 days)
From 2026:     after:2026-01-01
From 2024:     after:2024-01-01
Custom range:  after:2024-12-01 before:2025-01-15
All time:      omit time filter entirely
```

**Examples:**
- User: "Search GitHub for claude-skills from 2026"
  → Query: `site:github.com claude-skills after:2026-01-01`

- User: "Find articles on AI agents from the past week"
  → Query: `AI agents after:<today - 7 days>`

- User: "site:news.ycombinator.com python performance"
  → Query: `site:news.ycombinator.com python performance`

### Step 3: Call SerpAPI

Call `mcp__rube__RUBE_MULTI_EXECUTE_TOOL`:

| Parameter | Value |
|---|---|
| `tools` | `[{"tool_slug": "SERPAPI_GOOGLE_LIGHT_SEARCH", "arguments": {"q": "<query>", "num": 20}}]` |
| `sync_response_to_workbench` | `false` |
| `memory` | `{}` |
| `current_step` | `"SEARCH"` |
| `thought` | `"Searching for <query>"` |

**Do NOT pass `session` or `session_id`.** This is stateless.

### Step 4: Parse Response

Response structure:

```json
{
  "results": [{
    "response": {
      "data": {
        "organic_results": [
          {
            "position": 1,
            "title": "Result Title",
            "link": "https://example.com/page",
            "displayed_link": "example.com › page",
            "snippet": "Brief description of the result...",
            "date": "Jan 17, 2026"
          }
        ],
        "search_metadata": {
          "created_at": "2026-02-08 07:33:33 UTC"
        }
      }
    }
  }]
}
```

**Access the results:**
- Title: `organic_results[i]['title']`
- URL: `organic_results[i]['link']`
- Date: `organic_results[i].get('date', 'N/A')`
- Snippet: `organic_results[i].get('snippet', '')`

**CRITICAL:** Not all results have a `date` field. Use `.get('date', '')` to avoid KeyError.

### Step 5: Format Output

Process results directly inline. No workbench needed — SerpAPI returns ≤20 results.

**Default format: Markdown table**

```
**Google Search: "<query>"** | <count> results | <time period> | <site filter if any>

| # | Title | URL | Date | Snippet |
|---|---|---|---|---|
| 1 | Title... | [Link](url) | Date | Snippet... |
```

Rules:
- Single summary line above table
- Truncate titles to 80 characters with "…"
- Truncate snippets to 100 characters with "…"
- Format dates as "Feb 3, 2026" (parse from result date if available)
- URL as `[Link](url)` markdown
- No numbering needed if SerpAPI already orders by relevance

**Alternative formats:**

- **List format:**
  ```
  1. **Title** — [Link](url) — Date — Snippet
  ```

- **JSON format:**
  ```json
  {
    "query": "...",
    "period": "...",
    "results": [
      {"title": "...", "url": "...", "date": "...", "snippet": "..."}
    ]
  }
  ```

- **CSV format:**
  ```
  #,Title,URL,Date,Snippet
  1,"Title",...
  ```

## Edge Cases

| Scenario | Response |
|---|---|
| No query | "Please provide a search term. Example: 'Search for claude-skills on GitHub'" |
| No results | "No results found for '[query]'. Try broadening your search or removing date filters." |
| Malformed date | Skip date in output or use "Date unknown" |
| Very long snippet | Truncate at 100 chars with "…" |
| Special characters in query | SerpAPI handles escaping; pass as-is |
| Connection error | "Search failed. Check that SerpAPI connection is active." |

## Token Optimization

**Target:** 1 tool call, 0 workbench calls, single inline response.

- No `RUBE_SEARCH_TOOLS` (pre-determined)
- No session management (stateless)
- No workbench processing (inline formatting)
- No preamble ("Sure, here are...", "I found...")
- Compact formatting (truncated fields, clean dates)
- Results in API order (no custom sorting unless requested)

## Common Patterns

### GitHub Search
```
User: "Find Claude Code skills on GitHub from January 2026"
Query: site:github.com claude code skills after:2026-01-01
```

### News/Recent Articles
```
User: "News about AI from the past week"
Query: AI news after:<today - 7 days>
```

### Specific Domain
```
User: "Best practices on Medium"
Query: site:medium.com best practices
```

### Date Range
```
User: "Machine learning articles from 2024"
Query: machine learning after:2024-01-01 before:2025-01-01
```
