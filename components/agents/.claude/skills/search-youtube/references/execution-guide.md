# YouTube Search — Detailed Execution Guide

## Pre-Determined Tools

**Do NOT call `RUBE_SEARCH_TOOLS`.** The required tools are fixed:

| Tool Slug | Purpose | Quota |
|---|---|---|
| `YOUTUBE_SEARCH_YOU_TUBE` | Find videos by query | 100 units |
| `YOUTUBE_GET_VIDEO_DETAILS_BATCH` | Get stats (views, likes) for video IDs | 1 unit per video |

Both are called via `mcp__rube__RUBE_MULTI_EXECUTE_TOOL`.

### Prerequisite: Load the Wrapper Tool

`RUBE_MULTI_EXECUTE_TOOL` is a deferred tool — it must be loaded before use. At the start of the skill, call:

```
ToolSearch(query="select:mcp__rube__RUBE_MULTI_EXECUTE_TOOL")
```

This is a one-time step per session. Skip if the tool is already loaded.

### RUBE_MULTI_EXECUTE_TOOL Required Parameters

Every call to `mcp__rube__RUBE_MULTI_EXECUTE_TOOL` **must** include:

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `tools` | array | YES | Array of `{tool_slug, arguments}` objects |
| `sync_response_to_workbench` | boolean | YES | Set `true` to save response for workbench processing |
| `memory` | object | YES | **Always include**, even as `{}`. Keys are app names, values are string arrays. |
| `current_step` | string | no | Short label like `"SEARCH"`, `"FETCH_STATS"` |
| `thought` | string | no | One-sentence rationale |

**Session handling:**
- **First call:** Do NOT pass `session` or `session_id`. Omit both.
- **Subsequent calls:** Pass `session_id` as a string (not an object) — extract from the first call's response.

## Optimal Flow (Optimized for Token Efficiency)

### Low Verbosity (Default)

```
Step 0: Load RUBE_MULTI_EXECUTE_TOOL (once per session)
  └─ ToolSearch with select:mcp__rube__RUBE_MULTI_EXECUTE_TOOL

Step 1-2: Parse request + Map parameters (inline)

Call 1: YOUTUBE_SEARCH_YOU_TUBE
  └─ Returns: video IDs, titles, descriptions, published dates, channels

Step 3-4: Extract IDs + Call YOUTUBE_GET_VIDEO_DETAILS_BATCH
  └─ Returns: viewCounts, statistics for all results
  └─ Sort by viewCount descending

Step 7: Format Output
  └─ Markdown table with all results
  └─ No AI analysis (table format saves 10K+ tokens)

Total API cost: ~8-10K tokens
```

**Total: 1 ToolSearch (once) + 2 Rube calls + 0 workbench calls**

### High Verbosity (Token-Optimized)

```
Step 0: Load RUBE_MULTI_EXECUTE_TOOL (once per session)

Calls 1-4: Same as low verbosity
  └─ Search, fetch stats, sort by views

Step 5.5: Confirm Analysis Scope (inline)
  └─ If result_count > 10:
     Ask: "Found N results. Analyze top 10 or all N?"
  └─ Default to analyzing top 10

Step 6: Analyze Videos (inline Claude, NOT workbench)
  └─ Single Claude prompt analyzing top N videos
  └─ Generate 1-sentence descriptions + 3-4 keywords
  └─ Return JSON with descriptions + keywords

Step 7-8: Format Output
  └─ List format for analyzed videos (top 10)
  └─ Table format for remainder (if >10 searched)

Total API cost: ~12-15K tokens (vs 30K+ with old approach)
```

**Total: 1 ToolSearch (once) + 2 Rube calls + 0 workbench calls**
**Savings: 50-60% token reduction vs. previous approach**

## Step 1: Parse User Request

Extract these parameters from the user's message:

- **query** (REQUIRED): The search term(s)
  - Examples: "rust programming", "ai agents", "home workout"
  - If missing or ambiguous, ASK the user before proceeding

- **period** (optional): Time filter
  - Default: "past month"
  - Natural language examples: "past 24 hours", "past week", "past year", "all time"
  - Can also handle: "from 2024-12-01 to 2025-01-15"

- **limit** (optional): Number of results to search
  - Default: 20
  - YouTube API caps at 50 per page — use `pageToken` for more

- **analysis_limit** (optional): Maximum videos to analyze (high verbosity only)
  - Default: 10
  - User can override: "analyze all", "top 5", "top 15", etc.
  - This optimizes token usage for large result sets

- **sort_by** (optional): Sort order
  - Default: "viewCount" (popularity)
  - Accepted values: "viewCount", "date", "relevance", "rating"

- **verbosity** (optional): Output detail level
  - Default: "low"
  - Triggers for HIGH: "verbose", "detailed", "in detail", "summary", "analyze", "description"
  - Low = compact table format (all results)
  - High = list format with AI descriptions + keywords (top 10 analyzed by default)

- **extra_columns** (optional): Additional fields (low verbosity only)
  - Only include if user explicitly requests
  - Examples: channel name, video duration, likes, description

## Step 2: Convert Time Period to ISO 8601

Calculate `publishedAfter` date string in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ):

```
Past 24 hours: today - 1 day
Past week:     today - 7 days
Past month:    today - 30 days
Past 3 months: today - 90 days
Past 6 months: today - 180 days
Past year:     today - 365 days
All time:      omit publishedAfter entirely
Custom range:  use both publishedAfter and publishedBefore
```

## Step 3: Map Sort Parameter

```
User Says        → API Parameter
"popularity"     → "viewCount"
"views"          → "viewCount"
"most viewed"    → "viewCount"
"trending"       → "viewCount"
"newest"         → "date"
"most recent"    → "date"
"date"           → "date"
"relevance"      → "relevance"
"relevant"       → "relevance"
"rating"         → "rating"
"highest rated"  → "rating"
```

Default (if no sort mentioned): `"viewCount"`

## Step 4: Execute — Call 1 (Search)

Call `mcp__rube__RUBE_MULTI_EXECUTE_TOOL` with these exact parameters:

| Parameter | Value |
|---|---|
| `tools` | `[{"tool_slug": "YOUTUBE_SEARCH_YOU_TUBE", "arguments": {"q": "<query>", "type": "video", "maxResults": 20, "order": "viewCount"}}]` |
| `sync_response_to_workbench` | `true` |
| `memory` | `{}` |
| `current_step` | `"SEARCH"` |
| `thought` | `"Searching YouTube for <query>"` |

**Do NOT pass `session` or `session_id` on the first call.**

**Response structure:**
```
items[].id.videoId       → video ID (string)
items[].snippet.title    → video title
items[].snippet.publishedAt → ISO date
items[].snippet.channelTitle → channel name
nextPageToken            → pagination token (if more results available)
```

**For >50 results:** Make additional search calls with `pageToken` from `nextPageToken`.

## Step 5: Execute — Call 2 (Batch Details)

Extract video IDs directly from the inline search response. Do NOT use a workbench call just to extract IDs — they are visible in the response at `items[].id.videoId`.

Call `mcp__rube__RUBE_MULTI_EXECUTE_TOOL` with these exact parameters:

| Parameter | Value |
|---|---|
| `tools` | `[{"tool_slug": "YOUTUBE_GET_VIDEO_DETAILS_BATCH", "arguments": {"id": ["vid1", "vid2", ...], "parts": ["snippet", "statistics"]}}]` |
| `sync_response_to_workbench` | `true` |
| `memory` | `{}` |
| `current_step` | `"FETCH_STATS"` |
| `thought` | `"Fetching view counts for N videos"` |

**Do NOT pass `session_id` unless you need session continuity for a multi-page workflow.**

**Response structure:**
```
items[].id                              → video ID
items[].snippet.title                   → title (use this, may differ from search)
items[].snippet.publishedAt             → ISO date (YYYY-MM-DDTHH:MM:SSZ)
items[].snippet.description             → first 200 chars sufficient for analysis
items[].snippet.channelTitle            → channel name
items[].statistics.viewCount            → string, convert to int
items[].statistics.likeCount            → string, OPTIONAL (use .get())
items[].statistics.commentCount         → string, OPTIONAL (use .get())
items[].contentDetails.duration         → ISO 8601 duration (if "contentDetails" in parts)
```

**CRITICAL: Optional fields.** `likeCount` and `commentCount` may be missing when disabled by the uploader. Always use `.get('likeCount', '0')` to avoid KeyError.

**Max 50 IDs per call.** Chunk larger lists into multiple calls.

**Sort by viewCount:** Sort results descending by `int(viewCount)` for default popularity sort.

## Step 5.5: Confirm Analysis Scope (High Verbosity Only)

**Skip this step if verbosity is LOW.**

After fetching stats, check if result count > `analysis_limit` (default: 10):

**If result_count ≤ analysis_limit:**
- Proceed directly to Step 6 (Analyze all)

**If result_count > analysis_limit:**
- Ask user: "Found N results. Analyze top 10 (fast) or all N (slower)?"
- If user confirms "all" or specifies different number:
  - Update `analysis_limit` to user's preference
  - Proceed to Step 6
- If user says "top 10" (or doesn't respond):
  - Cap analysis to 10 videos
  - Show remainder as simple table in final output

**Example:**
```
Found 20 results. Analyze top 10 for faster results,
or analyze all 20 (slower, uses more tokens)?
[User: "just top 10"]
```

**Why:** Analyzing >10 videos with AI descriptions burns significant tokens. This cap optimizes cost while prioritizing the most relevant (top by viewCount) results.

## Step 6: Analyze Videos with AI (High Verbosity Only)

**Skip this step if verbosity is LOW or analysis_limit = 0.**

Analyze the top N videos (default: 10, user may override in Step 5.5) **INLINE using Claude**.

### Key Changes from Previous Approach

- ✅ **Do NOT use workbench for LLM calls** (saves 7K tokens)
- ✅ **Batch all N videos into a SINGLE Claude prompt** (saves 3K tokens)
- ✅ **Use simple 1-sentence descriptions** instead of 1-2 sentences (saves tokens)
- ✅ **Use 3-4 keywords** instead of 5 (saves tokens)

### Inline Analysis Prompt

After fetching stats, create this prompt for Claude (inline, not workbench):

```
Analyze these {N} YouTube videos about {topic}.

For each video, generate:
1. One sentence describing what's unique/distinctive about it
2. 3-4 topic hashtags (lowercase, no spaces)

Videos to analyze (sorted by views):
{formatted list with title + short description}

Return ONLY valid JSON (no markdown, no code blocks):
[
  {
    "description": "One sentence about what makes this unique",
    "keywords": ["#tag1", "#tag2", "#tag3"]
  },
  ...
]
```

### Description Guidelines

**Format:** One sentence max, specific and distinctive

**Good examples:**
- "Live coding demo of multi-agent orchestration with production patterns."
- "Beginner-friendly introduction to agent skills and autonomous workflows."
- "In-depth comparison of agent frameworks with performance benchmarks."
- "Quick setup guide revealing hidden configuration tricks."

**Bad examples:**
- "A tutorial about agents" (too generic)
- "This video covers X and Y and Z" (too long, not distinctive)
- "The best agent framework guide" (subjective, not distinctive)

**Duration:** One sentence = 10-20 tokens per video (vs 40+ for 1-2 sentences)

### Keyword Extraction Guidelines

- **3-4 hashtags** per video (not 5)
- **Lowercase** all hashtags
- **Hyphens** for multi-word: `#multi-agent`, `#live-coding`
- **Technical terms only**: `#agents`, `#llm`, `#orchestration`, `#deployment`
- **Content type tags OK**: `#tutorial`, `#demo`, `#comparison`, `#setup-guide`
- **Avoid generic**: No `#video`, `#2025`, `#great`, `#watch-this`

**Examples:**
- `["#agents", "#orchestration", "#deployment", "#production"]` ✓
- `["#agents", "#orchestration", "#deployment", "#awesome"]` ✗ (subjective)

### Performance Impact

For N=10 videos:
- Previous approach: 4 separate invoke_llm calls = 12K tokens
- New approach: 1 inline Claude prompt = 3-4K tokens
- **Savings: 8K tokens (67% reduction)**

## Step 7: Format Output (Inline)

### Low Verbosity: Markdown Table

```
**YouTube Search: "<query>"** | <count> results | <time period> | Sorted by <sort>

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 1 | Title 1 | [Link](url) | 2025-01-20 | 2.3M |
| 2 | Title 2 | [Link](url) | 2025-01-18 | 445K |
```

Rules:
- Single summary line above table (no preamble)
- Truncate titles at 80 chars with "…"
- Compact view counts (see view-count-formatting.md)
- YYYY-MM-DD dates
- Sort by int(viewCount) descending for popularity

### High Verbosity: List Format

```markdown
**YouTube Search: "<query>"** | <count> results | <time period> | Sorted by <sort>

**1. Title** — [Link](url) — 2025-01-20 — 890K views
Description sentence one. Description sentence two (optional).
Topics: #keyword1 #keyword2 #keyword3 #keyword4 #keyword5

**2. Title** — [Link](url) — 2025-01-18 — 445K views
[Based on title/description] Brief analysis from metadata.
Topics: #keyword1 #keyword2 #keyword3
```

**Formatting rules:**
- Bold number + title on first line
- Em dashes (—) separating link, date, views
- Description on line 2 (no blank line)
- Topics on line 3 (no blank line)
- Blank line between video entries
- Mark metadata-based analysis clearly

### Alternative Formats (if requested)

**JSON (low verbosity):**
```json
{"query": "...", "results": [...]}
```

**JSON (high verbosity):**
```json
{
  "query": "...",
  "results": [
    {
      "rank": 1,
      "title": "...",
      "url": "...",
      "date": "2025-01-20",
      "views": 890000,
      "description": "...",
      "topics": ["#tag1", "#tag2"]
    }
  ]
}
```

**CSV (low verbosity):**
```csv
#,Title,URL,Date,Views
1,"Title",https://...,2025-01-20,890000
```

**CSV (high verbosity):**
```csv
#,Title,URL,Date,Views,Description,Topics
1,"Title",https://...,2025-01-20,890000,"Description text","#tag1 #tag2 #tag3"
```

## Step 8: Hybrid Output (High Verbosity with >10 Results)

If user requested high verbosity but result_count > analysis_limit:

```
**YouTube Search: "query"** | 20 results (top 10 analyzed) | Past month | Sorted by popularity

[Analyzed videos 1-10 with descriptions + keywords]

**Remaining results (11-20):**

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 11 | Title | [Link](url) | 2025-01-15 | 234K |
| 12 | Title | [Link](url) | 2025-01-12 | 189K |
```

This balances token efficiency with completeness.

## Step 9: Handle Edge Cases

| Scenario | Response |
|---|---|
| No query | Ask user for search term |
| No results | "No videos found for '[query]' in [period]. Try broadening your search." |
| Fewer than requested | Show available + note: "Showing N of X requested results." |
| MCP error | "YouTube search failed. Check that youtube-automation MCP server is running." |
| Conflicting sort | Ask: "Sort by date or popularity?" |

## Ready-to-Use Workbench Snippets

### Low Verbosity: Format Table

Use this with `RUBE_REMOTE_WORKBENCH` when processing >20 results. For ≤20, format inline.

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

    # Compact view count formatting
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

### High Verbosity: Complete Workflow

Combines transcript fetching, analysis, and formatting in one workbench call:

```python
from youtube_transcript_api import YouTubeTranscriptApi
import json

# Inputs: video details from Step 5 + analysis parameters
video_data = [
    {"id": "abc123", "title": "...", "date": "2025-01-20", "views": 890000, "snippet": {...}},
    # ... more videos
]

results = []

for video in video_data:
    vid_id = video['id']
    title = video['title'][:77] + '…' if len(video['title']) > 80 else video['title']
    date = video['date'][:10]
    views = video['views']

    # Format view count
    if views >= 1_000_000:
        v = views / 1_000_000
        vs = f"{v:.1f}M" if v < 10 else f"{int(v)}M"
    elif views >= 1_000:
        v = views / 1_000
        vs = f"{v:.1f}K" if v < 10 else f"{int(v)}K"
    else:
        vs = str(views)

    # Try to fetch transcript
    transcript_text = None
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(vid_id)
        full_text = " ".join([entry['text'] for entry in transcript_list])
        transcript_text = full_text[:5000] if len(full_text) > 5000 else full_text
    except:
        pass

    # Generate description and keywords
    # (In practice, you'd use Claude for this analysis via inline processing)
    # This snippet shows the structure only

    if transcript_text:
        # Analyze transcript (this would be done by Claude inline)
        description = "Analyze and generate description based on transcript"
        based_on_metadata = False
    else:
        # Fall back to metadata
        description = f"Based on title and description: {video['snippet']['description'][:100]}"
        based_on_metadata = True

    # Extract keywords (simplified - would be done by Claude)
    keywords = ["#keyword1", "#keyword2", "#keyword3"]

    results.append({
        "title": title,
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "date": date,
        "views_formatted": vs,
        "description": description,
        "keywords": keywords,
        "based_on_metadata": based_on_metadata
    })

# Output formatted results
for i, r in enumerate(results, 1):
    prefix = "[Based on title/description] " if r['based_on_metadata'] else ""
    print(f"**{i}. {r['title']}** — [Link]({r['url']}) — {r['date']} — {r['views_formatted']} views")
    print(f"{prefix}{r['description']}")
    print(f"Topics: {' '.join(r['keywords'])}")
    print()  # Blank line between entries
```

**Note:** The actual transcript analysis should be done inline by Claude after fetching transcripts, not in the workbench. The workbench is only used for fetching transcripts and formatting final output.


## Token Optimization Checklist

### Both Verbosity Levels (All Searches)

- [ ] `ToolSearch` called once to load `RUBE_MULTI_EXECUTE_TOOL` (skip if already loaded)
- [ ] No `RUBE_SEARCH_TOOLS` call (tools are pre-determined)
- [ ] `memory: {}` included in every `RUBE_MULTI_EXECUTE_TOOL` call
- [ ] No `session` or `session_id` on first Rube call
- [ ] No workbench call just to extract video IDs
- [ ] No preamble text ("Sure, here are...", "I found...")
- [ ] Single summary line above results
- [ ] Compact number formatting (1.2M not 1,200,000)
- [ ] Truncated titles (80 char max)
- [ ] Clean date format (YYYY-MM-DD)
- [ ] URL as `[Link](url)` not raw URL
- [ ] `.get()` used for optional statistics fields

### Low Verbosity Only

- [ ] Table format (compact, efficient)
- [ ] No AI analysis performed
- [ ] All results shown (no limit)
- [ ] No workbench calls (except rare formatting for >20 results)

### High Verbosity (Token-Optimized)

- ✅ **Analysis done INLINE (not in workbench LLM calls)**
- ✅ **Limit analysis to top 10 by default**
- ✅ **Ask user confirmation if >10 results to analyze**
- ✅ **Single Claude prompt for all videos (not 4 separate calls)**
- [ ] Descriptions are 1 sentence max (not 1-2 sentences)
- [ ] 3-4 hashtags per video (not 5)
- [ ] Lowercase hashtags with hyphens: `#multi-agent`, `#live-coding`
- [ ] Blank lines between analyzed videos
- [ ] Show remainder as simple table if >10 results
- [ ] **NO workbench calls for LLM analysis**

### Skip These (Token Waste)

- ❌ NO transcript fetching (unavailable for recent videos)
- ❌ NO invoke_llm calls in workbench (do inline instead)
- ❌ NO multiple batched LLM calls (use 1 call for all)
- ❌ NO 1-2 sentence descriptions (use 1 max)
- ❌ NO 5 keywords per video (use 3-4)

## Common User Requests

| User Request                                          | How to Handle                                    | Token Cost |
| --------------------------------------------------- | ------------------------------------------------ | --------- |
| "Search YouTube for [term]"                         | Standard search, low verbosity (default)         | 8-10K |
| "Show me 5 results"                                 | Parse limit = 5                                  | 8-10K |
| "From the past week"                                | Parse period = "past week"                       | same |
| "Sort by newest"                                    | Parse sort_by = "date"                           | same |
| "Include channel names"                             | Add Channel column (low verbosity only)          | +1K |
| "As a JSON list"                                    | Output in JSON format                            | same |
| "Just the top 3"                                    | Set limit = 3                                    | 8-10K |
| "All time results"                                  | Omit publishedAfter filter                       | same |
| "From 2024"                                         | Parse custom date range                          | same |
| **High Verbosity Requests:**                        | **Analyze top 10 by default**                    | **+4-5K** |
| "Search for [term] with detailed descriptions"     | Inline Claude analysis, 1-sentence descriptions  | 12-15K |
| "[term] - detailed/verbose output"                 | Ask user to confirm if >10 results               | 12-15K |
| "Help me decide which [term] videos to watch"      | AI analysis of top results                       | 12-15K |
| "[term] - what makes each unique"                  | Show distinctive features of top 10              | 12-15K |
| "Search all [term] videos with analysis"           | High verbosity, confirm if >10 to analyze all    | +8K/10 |

**Token Cost Notes:**
- Low verbosity: ~8-10K (2 API calls only)
- High verbosity (top 10): ~12-15K (2 API calls + 1 inline Claude prompt)
- High verbosity (all 20+): ~20-25K (ask user first)

---

## Output Formats

## Overview

YouTube search skill supports two verbosity levels:
- **Low (default):** Compact table format optimized for quick scanning
- **High:** Enhanced list format with descriptions and keywords

## Low Verbosity (Default)

### Format Specification

Single summary line followed by markdown table:

```markdown
**YouTube Search: "<query>"** | <count> results | <time period> | Sorted by <sort>

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 1 | Title | [Link](url) | YYYY-MM-DD | Views |
```

### Column Specifications

| Column | Width | Format | Notes |
|---|---|---|---|
| # | Auto | Integer | 1-indexed sequence number |
| Video Title | 80 chars max | Text | Truncate with "…" if longer |
| URL | Auto | `[Link](url)` | Format as markdown link |
| Date | 10 chars | YYYY-MM-DD | ISO date from publishedAt |
| Views | Variable | Compact | 1.2M, 350K, 5.1K, or 890 |

### View Count Formatting

See `view-count-formatting.md` for detailed rules. Quick reference:

| Range | Format | Examples |
|---|---|---|
| ≥10M | `XM` | `12M`, `45M` |
| 1M-9.9M | `X.XM` | `1.2M`, `8.7M` |
| ≥10K | `XK` | `12K`, `890K` |
| 1K-9.9K | `X.XK` | `1.2K`, `5.8K` |
| <1K | `X` | `890`, `42` |

### Token Efficiency Rules

1. **No preamble** - Start directly with summary line
2. **No trailing analysis** - Table only unless user requests commentary
3. **Single summary line** - One line above table, not paragraphs
4. **Compact numbers** - Never raw numbers like 1,200,000
5. **Truncate titles** - Max 80 chars with "…"
6. **Minimal columns** - Only essentials unless user requests more

### Example Output

```markdown
**YouTube Search: "rust programming tutorials"** | 20 results | Past month | Sorted by popularity

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 1 | Rust Full Course 2025 — Beginner to Advanced | [Link](https://www.youtube.com/watch?v=abc123) | 2025-01-20 | 890K |
| 2 | 10 Rust Features You Didn't Know About | [Link](https://www.youtube.com/watch?v=def456) | 2025-01-18 | 445K |
| 3 | Building a CLI Tool in Rust | [Link](https://www.youtube.com/watch?v=ghi789) | 2025-01-15 | 234K |
```

**Token count:** ~50-70 tokens per video in table format

## High Verbosity (Token-Optimized)

### Format Specification

Summary line followed by numbered list entries with concise descriptions and keywords. **By default analyzes top 10 results only** to optimize token usage.

```markdown
**YouTube Search: "<query>"** | 20 results (top 10 analyzed) | <time period> | Sorted by <sort>

**1. Title** — [Link](url) — YYYY-MM-DD — 890K views
One sentence highlighting what's distinctive about this video.
Topics: #keyword1 #keyword2 #keyword3

**2. Title** — [Link](url) — YYYY-MM-DD — 445K views
...

[If >10 results exist, show remainder as table:]

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 11 | Title | [Link](url) | 2025-01-15 | 234K |
| 12 | Title | [Link](url) | 2025-01-12 | 189K |
```

### Entry Structure

Each video entry has three lines:
1. **Title line:** Bold number + title + link + date + views (all inline)
2. **Description:** 1-2 sentences highlighting unique aspects
3. **Topics:** 3-5 hashtags representing key topics

### Title Line Format

```
**N. Title Text** — [Link](url) — YYYY-MM-DD — Views
```

**Components:**
- `**N.**` - Bold number with period
- Space + title text (max 80 chars, truncate with "…")
- ` — ` - Em dash surrounded by spaces
- `[Link](url)` - Markdown link
- ` — ` - Em dash surrounded by spaces
- Date in YYYY-MM-DD
- ` — ` - Em dash surrounded by spaces
- Compact view count

### Description Guidelines (Token-Optimized)

- **1 sentence maximum** (not 1-2, to save tokens)
- Focus on **what makes this video distinctive**
- Be specific about the unique angle or focus
- Avoid generic summaries or restating title
- Examples:
  - "Live demo of multi-agent orchestration with production patterns."
  - "Beginner-friendly intro with step-by-step debugging examples."
  - "Compares 3 frameworks with performance benchmarks."

### Topics Guidelines (Token-Optimized)

- **3-4 hashtags** per video (not 5, to save tokens)
- **Lowercase** all hashtags
- **Hyphens** for multi-word concepts: `#multi-agent`, `#live-coding`
- **No spaces** in hashtags
- **Technical terms only**: `#agents`, `#orchestration`, `#deployment`
- **Content type OK**: `#tutorial`, `#demo`, `#comparison`
- **Avoid generic**: No `#video`, `#2025`, `#great`, `#awesome`

### Spacing Rules

```
**YouTube Search: "query"** | 10 results (top 10 analyzed) | <period> | Sorted by <sort>

**1. Title...** — [Link](...) — YYYY-MM-DD — Views
One sentence description.
Topics: #tag1 #tag2 #tag3

**2. Title...** — [Link](...) — YYYY-MM-DD — Views
One sentence description.
Topics: #tag1 #tag2 #tag3
```

- Blank line after summary header
- No blank line between title and description
- No blank line between description and topics
- Single blank line between video entries

### Example Output (Token-Optimized)

```markdown
**YouTube Search: "claude ai agent frameworks"** | 15 results (top 10 analyzed) | Past month | Sorted by popularity

**1. Building Multi-Agent Systems with Claude** — [Link](https://www.youtube.com/watch?v=abc123) — 2025-01-20 — 890K views
Deep dive on orchestration and production deployment patterns for multi-agent systems.
Topics: #multi-agent #orchestration #production #deployment

**2. Claude AI Tutorial for Beginners** — [Link](https://www.youtube.com/watch?v=def456) — 2025-01-18 — 445K views
Beginner-friendly intro with live coding examples and step-by-step debugging.
Topics: #tutorial #beginner #live-coding #debugging

**3. LangGraph vs Custom Agent Frameworks** — [Link](https://www.youtube.com/watch?v=ghi789) — 2025-01-15 — 234K views
Comparative analysis of agent frameworks with performance metrics and cost breakdowns.
Topics: #langgraph #comparison #benchmarks #performance

[... videos 4-10 ...]

**Remaining results (11-15):**

| # | Video Title | URL | Date | Views |
|---|---|---|---|---|
| 11 | Advanced Agent Patterns | [Link](url) | 2025-01-12 | 189K |
| 12 | Agent Failures and Recovery | [Link](url) | 2025-01-10 | 145K |
```

**Token count:** ~60-80 tokens per analyzed video (1/3 of old format)
- Savings: 1-sentence descriptions vs 1-2 sentences (-30% per video)
- Savings: 3-4 keywords vs 5 (-20% per video)
- **Total: 50% token reduction in verbose output**
- **Default 10 videos: further 50% reduction if user has more results**

## Format Selection

### Use Low Verbosity When:
- User doesn't specify verbosity
- Quick scanning is the goal
- User is familiar with the topic
- Token efficiency is critical
- Large result sets (>20 videos)

### Use High Verbosity When:
User request includes keywords:
- "verbose", "verbose output"
- "detailed", "in detail"
- "summary", "summaries"
- "transcript", "transcript analysis"
- "analyze", "analysis"
- "description", "descriptions"
- "what makes each unique"
- "help me decide which to watch"

### Verbosity Detection Examples

| User Request | Verbosity | Reason |
|---|---|---|
| "Search YouTube for rust tutorials" | Low | No verbosity keywords |
| "Find detailed rust tutorials" | High | "detailed" keyword |
| "Search for AI agents with transcript analysis" | High | "transcript" keyword |
| "Show me Python videos, verbose output" | High | "verbose" keyword |
| "Top 5 React videos in detail" | High | "in detail" keyword |
| "Latest JavaScript news" | Low | No verbosity keywords |

## Token Efficiency Comparison (Optimized)

### Low Verbosity (Table) — Default
- Summary line: ~15-20 tokens
- Per video: ~40-50 tokens
- 20 videos: ~800-1,000 tokens total
- **Total request: ~8-10K tokens** (with API calls)

### High Verbosity (List) — Top 10 Only
- Summary line: ~15-20 tokens
- Per analyzed video: ~60-80 tokens (title ~50 + description ~20 + keywords ~10-20)
- 10 analyzed videos: ~600-800 tokens
- Remainder (simple table): ~400-500 tokens
- **Total request: ~12-15K tokens** (with API calls)
- **Savings vs old approach: 50-60% reduction** (was ~30-33K)

### High Verbosity (List) — All 20 Videos (User Opt-In)
- Summary line: ~15-20 tokens
- 20 analyzed videos: ~1,200-1,600 tokens
- **Total request: ~18-22K tokens** (with API calls)
- **Still 30-35% more efficient** than previous approach
- **Only done if user explicitly requests**

### Cost Comparison: Old vs New

| Scenario | Old Approach | New Approach | Savings |
|----------|-------------|--------------|---------|
| Low verbosity | 8-10K | 8-10K | 0% (same) |
| High verbosity (10 vids) | 18-20K | 12-15K | **30-40%** |
| High verbosity (20 vids) | 30-33K | 18-22K | **40-50%** |
| High verbosity (20 vids, full) | 30-33K | 20-25K | **25-35%** |

**Trade-off:** Shorter descriptions (1 sentence instead of 1-2) and fewer keywords (3-4 instead of 5), but vastly more efficient. Users still get the key information to decide which videos to watch.

## Alternative Formats (Both Verbosity Levels)

### JSON Format

```json
{
  "query": "search term",
  "time_period": "past month",
  "sort_order": "popularity",
  "result_count": 20,
  "results": [
    {
      "rank": 1,
      "title": "Video Title",
      "url": "https://www.youtube.com/watch?v=abc123",
      "date": "2025-01-20",
      "views": 890000,
      "views_formatted": "890K",
      "description": "...",  // Only in high verbosity
      "topics": ["#tag1", "#tag2"]  // Only in high verbosity
    }
  ]
}
```

### CSV Format

**Low verbosity:**
```csv
Rank,Title,URL,Date,Views
1,"Video Title",https://www.youtube.com/watch?v=abc123,2025-01-20,890000
```

**High verbosity:**
```csv
Rank,Title,URL,Date,Views,Description,Topics
1,"Video Title",https://...,2025-01-20,890000,"Description text","#tag1 #tag2 #tag3"
```

### List Format (Plain Text)

**Low verbosity:**
```
1. Video Title — https://www.youtube.com/watch?v=abc123 — 2025-01-20 — 890K views
2. ...
```

**High verbosity:**
```
1. Video Title — https://www.youtube.com/watch?v=abc123 — 2025-01-20 — 890K views
   Description text here.
   Topics: #tag1 #tag2 #tag3

2. ...
```

## Quality Checklist

Before outputting results:

**Low verbosity:**
- [ ] Single summary line (no preamble)
- [ ] Clean markdown table
- [ ] Titles truncated at 80 chars
- [ ] Dates in YYYY-MM-DD format
- [ ] View counts compacted (1.2M not 1,200,000)
- [ ] Links formatted as `[Link](url)`
- [ ] No trailing analysis

**High verbosity:**
- [ ] All low verbosity checks
- [ ] List format with proper spacing
- [ ] 1-2 sentence descriptions per video
- [ ] Descriptions focus on unique aspects
- [ ] 3-5 hashtags per video
- [ ] Hashtags lowercase, no spaces
- [ ] Metadata-based analysis marked clearly
- [ ] Blank lines between entries
