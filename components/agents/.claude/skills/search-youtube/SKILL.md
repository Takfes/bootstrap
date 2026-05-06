---
name: search-youtube
description: Search YouTube videos with customizable filters (time period, result count, sort order, verbosity). Use when users request YouTube searches with natural language queries like "find videos about [topic]", "search for [query] from the past week", or "show me top videos on [subject]". Returns results in two modes - compact table format (default) or enhanced list format with transcript-based descriptions and topic keywords when users want detailed analysis or help deciding which videos to watch.
---

# YouTube Search

## Overview

Search YouTube videos efficiently using the youtube-automation skill. Returns structured results with customizable filters for time period, result count, sort order, and verbosity level.

**Two verbosity modes:**
- **Low (default):** Compact table format for quick scanning (all results)
- **High:** Enhanced list format with AI-generated descriptions and topic keywords (top 10 by default)

Use high verbosity when users want to understand what makes each video unique or need help deciding which videos to watch. **Note:** High verbosity defaults to analyzing the top 10 results to optimize token usage; for larger result sets, you'll be asked whether to analyze all results.

## Quick Start

Basic usage with all defaults (past month, 20 results, sorted by popularity):

```
User: "Search YouTube for rust programming tutorials"

Output:
**YouTube Search: "rust programming tutorials"** | 20 results | Past month | Sorted by popularity

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 1 | Rust Full Course 2025 — Beginner to Advanced | [Link](https://www.youtube.com/watch?v=abc123) | 2025-01-20 | 890K |
| 2 | 10 Rust Features You Didn't Know About | [Link](https://www.youtube.com/watch?v=def456) | 2025-01-18 | 445K |
```

## Customizable Parameters

Users can override defaults inline in their request:

| Parameter     | Default            | Override Examples                                     |
| ------------- | ------------------ | ----------------------------------------------------- |
| Time Period   | Past 1 month       | "past week", "past 24 hours", "past year", "all time" |
| Result Count  | 20                 | "show 5 results", "top 50 videos" (override with `limit`) |
| Sort Order    | Popularity (views) | "sort by date", "sort by relevance", "sort by rating" |
| Verbosity     | Low                | "verbose", "detailed", "in detail", "with descriptions", "analyze transcripts" |
| Output Format | Auto (by verbosity)| "as a list", "JSON format", "CSV"                     |

## Token Optimization Rules

1. **No preamble** - Skip "Sure, here are the results" and similar filler
2. **Single summary line** - One line header above results, not paragraphs
3. **Compact numbers** - Format view counts as 1.2M, 350K, 5.1K, or 890 (no raw numbers)
4. **Truncate titles** - Max 80 characters, append "…" if longer
5. **Clean dates** - Always YYYY-MM-DD format
6. **Minimal columns** - Only title, URL, date, views unless user requests more
7. **No analysis** - Return results only unless explicitly asked for commentary

## Execution Workflow

**IMPORTANT:**
- **Do NOT call `RUBE_SEARCH_TOOLS`** — the tool slugs and schemas are pre-determined below.
- **Prerequisite:** `RUBE_MULTI_EXECUTE_TOOL` must be loaded before use. Call `ToolSearch` with `select:mcp__rube__RUBE_MULTI_EXECUTE_TOOL` once at the start if it hasn't been loaded in this session.
- **Target: 2 Rube calls + 0-1 workbench calls.** No more.

### 1. Parse User Request

Extract:

- **query** (REQUIRED): The search term(s) - ask if missing or ambiguous
- **period** (optional): Time filter — default: "past month"
- **limit** (optional): Number of results to search — default: 20
- **analysis_limit** (optional): For high verbosity only — max videos to analyze — default: 10
- **sort_by** (optional): Sort order — default: "viewCount"
- **verbosity** (optional): Output detail level — default: "low"
  - **Triggers for HIGH:** "verbose", "detailed", "in detail", "summary", "analyze", "description", "what makes each unique", "help me decide"
  - **Low:** Table format with all results
  - **High:** List format with AI descriptions + keywords (top 10 videos analyzed by default)
- **extra_columns** (optional): Channel, duration, description, etc. if requested (low verbosity only)

### 2. Map Parameters

**Time period → ISO 8601 `publishedAfter`:**

| User Says     | publishedAfter |
| ------------- | -------------- |
| past 24 hours | now - 1 day    |
| past week     | now - 7 days   |
| past month    | now - 30 days  |
| past 3 months | now - 90 days  |
| past 6 months | now - 180 days |
| past year     | now - 365 days |
| all time      | omit entirely  |

**Sort → YouTube API `order`:**

| User Says  | API value   |
| ---------- | ----------- |
| popularity | viewCount   |
| date       | date        |
| relevance  | relevance   |
| rating     | rating      |

### 3. Call 1: Search Videos

Call `mcp__rube__RUBE_MULTI_EXECUTE_TOOL` with these exact parameters:

- `tools`: `[{"tool_slug": "YOUTUBE_SEARCH_YOU_TUBE", "arguments": {"q": "<search_term>", "type": "video", "maxResults": <int, max 50>, "order": "<sort_param>"}}]`
  - Note: `maxResults` is the YouTube API parameter; the user-facing parameter is `limit`
- `sync_response_to_workbench`: `true`
- `memory`: `{}` **(REQUIRED — always include, even if empty)**
- `current_step`: `"SEARCH"`
- `thought`: `"Searching YouTube for <query>"`

**Do NOT pass `session` or `session_id` on the first call.** The response will return a session ID — use it in subsequent calls.

**Note:** YouTube search API maxResults caps at 50. For >50 results, use `pageToken` from the response's `nextPageToken` in a follow-up call.

**Response structure:** Video IDs are at `items[].id.videoId`. Titles at `items[].snippet.title`. Dates at `items[].snippet.publishedAt`. The search endpoint does NOT return view counts — that requires Step 4.

### 4. Call 2: Get Video Statistics

Extract video IDs directly from the inline search response (do NOT use a workbench call just to extract IDs). Then call `mcp__rube__RUBE_MULTI_EXECUTE_TOOL` with:

- `tools`: `[{"tool_slug": "YOUTUBE_GET_VIDEO_DETAILS_BATCH", "arguments": {"id": ["<vid1>", "<vid2>", ...], "parts": ["snippet", "statistics"]}}]`
- `sync_response_to_workbench`: `true`
- `memory`: `{}` **(REQUIRED)**
- `current_step`: `"FETCH_STATS"`
- `thought`: `"Fetching view counts for N videos"`

**Response structure:** Each item has:
- `item['id']` — video ID
- `item['snippet']['title']` — title
- `item['snippet']['publishedAt']` — ISO date
- `item['statistics']['viewCount']` — string, convert to int for sorting
- `item['statistics'].get('likeCount', '0')` — OPTIONAL, may be missing
- `item['statistics'].get('commentCount', '0')` — OPTIONAL, may be missing

**CRITICAL:** Always use `.get()` for `likeCount` and `commentCount` — they can be missing when disabled by the uploader.

### 5. Confirm Analysis Scope (High Verbosity Only)

**Skip this step if verbosity is LOW.**

If verbosity is HIGH:
1. Sort results by viewCount (already done in Step 4)
2. If result count > analysis_limit (default: 10):
   - Ask user: "Found N results. Analyze top 10 for faster results, or all N (slower)?"
   - Wait for user confirmation before proceeding
3. Cap analysis to the requested scope (default 10, user can override)

**Why this matters:** Analyzing 20+ videos with AI descriptions burns significant tokens. Limiting to top 10 (most relevant) is the most efficient approach.

### 5.5. Fetch Transcripts (Optional, High Verbosity Only)

**Skip this step if:**
- Verbosity is LOW
- Videos were published < 14 days ago (transcripts often unavailable)
- User hasn't explicitly requested transcript analysis

For older videos (14+ days old), optionally fetch transcripts to improve descriptions. This is non-critical—metadata-based analysis is sufficient.

### 6. Analyze Videos with AI (High Verbosity Only)

**Skip this step if verbosity is LOW or analysis_limit = 0.**

Analyze the top N videos (default: 10) using Claude inline (NOT in workbench):

For each video, generate:
1. **1-sentence description** highlighting what makes it distinctive:
   - Focus on unique aspects vs other results
   - Keep concise: one clear, specific insight
   - Template: "Covers [topic] with focus on [unique angle]."
   - Examples:
     - "Covers agent architectures with emphasis on production deployment patterns."
     - "Live coding demo of multi-agent workflows with real debugging."
     - "Beginner-friendly introduction to tool use and orchestration."

2. **3-4 topic keywords as hashtags:**
   - Lowercase, hyphens for multi-word
   - Represent actual technical topics
   - Examples: `#agents`, `#multi-agent`, `#deployment`, `#live-coding`

**DO THIS INLINE:** Batch all N videos into a single Claude prompt (don't use workbench). This is more efficient and uses current conversation context.

Example prompt structure:
```
Analyze these N YouTube videos about [topic]. For each:
1. One sentence describing what's unique about it
2. 3-4 hashtags for topics covered

Videos:
[title + description for each]

Return JSON: [{"description": "...", "keywords": ["#tag1", "#tag2"]}]
```

### 7. Format Output

Format results inline based on verbosity level.

**Low verbosity (default):** Markdown table with all results, summary header.

```markdown
**YouTube Search: "query"** | 20 results | Past month | Sorted by popularity

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 1 | Title | [Link](url) | 2025-01-20 | 890K |
| 2 | Title | [Link](url) | 2025-01-18 | 445K |
```

**High verbosity:** List format with analyzed videos (top N only), plain table for remainder.

```markdown
**YouTube Search: "query"** | 20 results (analyzing top 10) | Past month | Sorted by popularity

**1. Title** — [Link](url) — 2025-01-20 — 890K views
One sentence highlighting distinctive approach or focus.
Topics: #tag1 #tag2 #tag3

**2. Title** — [Link](url) — 2025-01-18 — 445K views
...

[If >10 results analyzed, show remainder as simple table:]

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 11 | Title | [Link](url) | 2025-01-15 | 234K |
| 12 | Title | [Link](url) | 2025-01-12 | 189K |
```

**Alternative formats (user-requested):**
- **JSON**: Raw array of objects with optional description/topics
- **CSV**: Comma-separated with headers, optional description/topics columns

### 8. Hybrid Output for Large High-Verbosity Searches

When user requests high verbosity for a search that returns >10 results:

1. Ask: "Found N results. Analyze top 10 (fast) or all N (slower)?"
2. If user says "all" or specifies higher number:
   - Analyze top 10 with full descriptions
   - Show remaining results as compact table
   - This balances token efficiency with completeness
3. If user says "top 10" (default):
   - Return only the 10 analyzed videos

### 9. Handle Edge Cases

- **No query**: Ask user to provide a search term
- **No results**: Return "No videos found for "[query]" in [time period]. Try broadening your search or extending the time range."
- **Fewer results than requested**: "Showing N of X requested results."
- **MCP server error**: Report concisely and suggest checking that youtube-automation is running

## Ready-to-Use Workbench Snippet

For processing batch details into a sorted table (use with `RUBE_REMOTE_WORKBENCH`):

```python
import json

with open('<workbench_file_path>', 'r') as f:
    file_data = json.load(f)

result_data = file_data['results'][0]['response']['data']
videos = []

for item in result_data['items']:
    vid = item['id']
    title = item['snippet']['title']
    date = item['snippet']['publishedAt'][:10]
    views = int(item['statistics'].get('viewCount', 0))

    # Compact view count
    if views >= 1_000_000:
        v = views / 1_000_000
        vs = f"{v:.1f}M" if v < 10 else f"{int(v)}M"
    elif views >= 1_000:
        v = views / 1_000
        vs = f"{v:.1f}K" if v < 10 else f"{int(v)}K"
    else:
        vs = str(views)

    videos.append((title[:77] + '…' if len(title) > 80 else title,
                    f"https://www.youtube.com/watch?v={vid}", date, vs, views))

videos.sort(key=lambda x: x[4], reverse=True)

print("| # | Video Title | URL | Date | Views |")
print("|---|---|---|---|---|")
for i, (t, u, d, vs, _) in enumerate(videos, 1):
    print(f"| {i} | {t} | [Link]({u}) | {d} | {vs} |")
```

## Verbosity Mode Examples

### Low Verbosity (Default)

```
User: "Search YouTube for rust programming tutorials"

Output:
**YouTube Search: "rust programming tutorials"** | 20 results | Past month | Sorted by popularity

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 1 | Rust Full Course 2025 — Beginner to Advanced | [Link](url) | 2025-01-20 | 890K |
| 2 | 10 Rust Features You Didn't Know About | [Link](url) | 2025-01-18 | 445K |
```

### High Verbosity

```
User: "Search YouTube for rust tutorials with detailed descriptions"

Output:
**YouTube Search: "rust tutorials"** | 10 results | Past month | Sorted by popularity

**1. Rust Full Course 2025 — Beginner to Advanced** — [Link](url) — 2025-01-20 — 890K views
Comprehensive coverage from basics to advanced concepts including ownership, lifetimes, and async. Distinguished by real-world project examples and production deployment patterns.
Topics: #rust #systems-programming #async #ownership #production

**2. 10 Rust Tips You Didn't Know** — [Link](url) — 2025-01-18 — 445K views
Collection of lesser-known Rust idioms and patterns for intermediate developers. Unique focus on compiler optimization tricks and unsafe code patterns.
Topics: #rust #tips #intermediate #optimization #unsafe
```

## References

See `references/execution-guide.md` for detailed technical specifications, examples, and output format specifications.

See `references/view-count-formatting.md` for number formatting rules.

## Related Skills

**Other search skills:** `/search-web` · `/search-zotero` · `/search-perplexity`
