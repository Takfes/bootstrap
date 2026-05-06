---
name: search-zotero
description: Search your Zotero library for academic papers with semantic or collection-based queries. Use when users request "find papers about [topic]", "search Research collection for [query]", "show me optimization papers", or "find articles on [subject]". Defaults to Research collection with 10 results. Returns structured output with titles, authors, years, zotero IDs, and full PDF paths for direct file access.
---

# Zotero Search

## Overview

Search your Zotero library efficiently for academic papers using semantic search (AI-powered embeddings) or collection-based filtering. Returns structured results with complete metadata including authors, publication year, Zotero attachment IDs, and full PDF paths for direct file access.

**Default behavior:**
- Collection: Research (configurable)
- Result limit: 10 (customizable, max 50)
- Abstracts: Not included (optional with `include_abstract=true`)
- Search strategy: Semantic search preferred, falls back to collection-based search

Use this skill when users want to explore their research library by topic, author, year, or specific keywords.

## Quick Start

Basic usage with all defaults (Research collection, 10 results, no abstracts):

```
User: "Find papers about graph neural networks in logistics"

Output:
**Zotero Search: "graph neural networks in logistics"** | 10 results | Research

| # | Title | Authors | Year | Zotero ID | PDF Path |
|---|---|---|---|---|---|
| 1 | Combinatorial Optimization with Graph Neural Networks | Liu, Y., Zhang, P., et al. | 2024 | M3ALTMQZ | /Users/takis/Zotero/storage/M3ALTMQZ/Liu_2024_Combinatorial_Optimization.pdf |
| 2 | Neural Networks for Vehicle Routing Problems | Chen, M., Wang, S. | 2023 | K7QWBXYZ | /Users/takis/Zotero/storage/K7QWBXYZ/Chen_Wang_2023_VRP.pdf |
```

## Customizable Parameters

Users can override defaults inline in their request:

| Parameter | Default | Override Examples |
|-----------|---------|-------------------|
| Query | (required) | Any search term or phrase |
| Collection | Research | "search Optimization collection", "use Papers collection" |
| Limit | 10 | "find 5 papers", "show 20 results" |
| Include Abstract | false | "include abstracts", "with summaries" |
| Search Mode | auto | "semantic search", "collection search", "use tags" |
| Enhance Query | auto | "with query enhancement", "as-is" |

## Token Optimization Rules

1. **No preamble** — Skip "Sure, here are the results" and similar filler
2. **Single summary line** — One-line header above results, not paragraphs
3. **Compact table** — Only necessary columns: #, Title, Authors, Year, Zotero ID, PDF Path
4. **Truncate titles** — Max 80 characters, append "…" if longer
5. **Compact authors** — Format as "Last, F., Last2, F." for first 3, then "et al." if more
6. **Clean years** — 4-digit year or "N/A"
7. **Minimal processing** — Return results inline (no workbench for <20 results)
8. **No analysis** — Return results only unless explicitly asked for commentary

## Execution Workflow

**IMPORTANT:**
- **Prerequisite:** Zotero MCP tools must be loaded. These are pre-determined and built into the Zotero MCP server.
- **Target: 3-5 tool calls total** — Collection lookup (cached), search, metadata fetch, attachment fetch.

### 1. Parse User Request

Extract:

- **query** (REQUIRED): The search term(s) — ask if missing or ambiguous
- **collection** (optional): Collection name — default: "Research"
- **limit** (optional): Number of results — default: 10, max: 50
- **include_abstract** (optional): Include abstract in output — default: false
- **search_mode** (optional): "auto" (default), "semantic", "collection", "tag"
- **enhance_query** (optional): Auto-enhance vague queries — default: true for queries <5 words or acronyms

**Vague query detection:**
- Triggers query enhancement if:
  - Query is <5 words (e.g., "RL", "optimization", "agents")
  - Query contains acronyms (e.g., "GNN", "RL", "VRP")
  - Query is generic (e.g., "papers", "research")

### 2. Load Zotero MCP Tools (Once Per Session)

Check if Zotero tools are already loaded in the conversation. If not, acknowledge that we're using the Zotero MCP server.

**Tools needed:**
- `mcp__zotero__zotero_get_collections` — List collections
- `mcp__zotero__zotero_semantic_search` — AI-powered search (preferred)
- `mcp__zotero__zotero_get_collection_items` — Collection-based search (fallback)
- `mcp__zotero__zotero_get_item_metadata` — Fetch item details (title, authors, year)
- `mcp__zotero__zotero_get_item_children` — Fetch attachments (PDF paths, keys)

### 3. Resolve Collection Name → Key

If not already cached:

1. Call `mcp__zotero__zotero_get_collections` to list available collections
2. Find collection by name (case-insensitive match)
3. Extract collection key (e.g., "L7DYN5N5" for "Research")
4. **Cache the key in conversation memory** for reuse in same session

**Cache format:**
```
{
  "zotero": [
    "Research collection key is L7DYN5N5",
    "Optimization collection key is K2QWBXYZ"
  ]
}
```

**If collection not found:**
- List available collections
- Ask user: "Collection '[name]' not found. Which collection would you like to search? Available: [list]"
- Re-run search with user's selection

### 4. Determine Search Strategy

**Auto mode (default):**

1. Try semantic search first (natural language, 3+ words)
2. If semantic search fails, falls back to collection-based search
3. Fall back to tag search only if user explicitly mentions tags

**Semantic search:** Better for natural language queries, returns ranked results by relevance

**Collection-based search:** Filter all items in collection by matching query against title/authors/year

**Tag search:** Filter by exact tag matches (only if user mentions tags)

### 5. Execute Search

Call the appropriate Zotero tool based on strategy:

**Semantic Search:**
```python
tool_slug: "mcp__zotero__zotero_semantic_search"
arguments: {
    "query": "<search_query>",
    "limit": <limit>,
    "filters": {} # optional: {"created_date_range": {...}} if user specifies date
}
```

**Response structure:**
- `items[]` — Array of matching items
- Each item: `{"key": "...", "title": "...", "creators": [...], "date": "..."}`

**Collection-based Search:**
```python
tool_slug: "mcp__zotero__zotero_get_collection_items"
arguments: {
    "collection_key": "<cached_key>",
    "limit": <limit>
}
```

**Response structure:**
- `items[]` — Array of items in collection
- Each item: `{"key": "...", "title": "...", "creators": [...]}`

**Filter inline:** Match query against item title/creators to rank and select top N results.

### 6. Fetch Metadata for Top Results

Call `mcp__zotero__zotero_get_item_metadata` for each result (parallel if possible):

```python
tool_slug: "mcp__zotero__zotero_get_item_metadata"
arguments: {
    "item_key": "<item_key>",
    "include_abstract": <boolean>,
    "format": "markdown"  # structured output
}
```

**Response structure:**
- `title` — Full title
- `creators` — Author list: `[{"firstName": "John", "lastName": "Doe", "creatorType": "author"}, ...]`
- `date` — Publication date (extract year as 4 digits)
- `itemType` — Type of item
- `abstract` — (optional) Only if `include_abstract=true`

### 7. Fetch Attachments (PDF Paths)

For each item, call `mcp__zotero__zotero_get_item_children` to get attachment details:

```python
tool_slug: "mcp__zotero__zotero_get_item_children"
arguments: {
    "item_key": "<item_key>"
}
```

**Response structure:**
- `children[]` — Array of child items (attachments, notes, etc.)
- Each child: `{"key": "...", "itemType": "attachment", "contentType": "application/pdf", "title": "..."}`

**Extract PDF info:**
- Look for `itemType: "attachment"` with `contentType: "application/pdf"`
- Get attachment key (e.g., "M3ALTMQZ")
- Get attachment title/filename

**Construct PDF path:**
```
{home}/Zotero/storage/{attachment_key}/{filename}
```

Platform-specific:
- macOS/Linux: `/Users/{username}/Zotero/storage/`
- Windows: `C:\Users\{username}\Zotero\storage\`

Use `os.path.expanduser("~")` for cross-platform compatibility.

### 8. Query Enhancement (Optional)

**Skip if `enhance_query=false` or query ≥5 words**

If query appears vague (<5 words, acronym, or generic):

1. Generate enhanced version:
   - Expand acronyms (e.g., "RL" → "reinforcement learning")
   - Add related terms (e.g., "optimization" → "optimization algorithms machine learning")
   - Add domain context (e.g., "agents" → "multi-agent systems agent architectures")

2. Ask user: "Enhanced query: '[new query]' — OK?"
   - If approved: Use enhanced query for search
   - If rejected: Search with original query

**Enhancement examples:**
- "RL" → "reinforcement learning deep Q-learning policy gradient"
- "GNN" → "graph neural networks graph convolution neural message passing"
- "optimization" → "combinatorial optimization machine learning heuristics"

### 9. Format Output

Format results inline based on `include_abstract`:

**Without abstracts (default):**

```markdown
**Zotero Search: "[query]"** | N results | [Collection name]

| # | Title | Authors | Year | Zotero ID | PDF Path |
|---|---|---|---|---|---|
| 1 | Title (max 80 chars) | Last, F., Last2, F., et al. | 2024 | M3ALTMQZ | /Users/takis/Zotero/storage/M3ALTMQZ/file.pdf |
| 2 | ... | ... | ... | ... | ... |
```

**With abstracts (if `include_abstract=true`):**

```markdown
**Zotero Search: "[query]" (with abstracts)** | N results | [Collection name]

| # | Title | Authors | Year | Abstract |
|---|---|---|---|---|
| 1 | Title | Authors | 2024 | Abstract text (truncated to 150 chars)… |
```

**Field format specifications:**
- **#:** 1-indexed sequence number
- **Title:** Truncate at 80 chars, append "…" if longer
- **Authors:** Format as "Last, F., Last2, F." for first 3 authors, then "et al." if more (comma-separated)
- **Year:** 4-digit year (e.g., 2024) or "N/A" if missing
- **Zotero ID:** Attachment key, e.g., "M3ALTMQZ"
- **PDF Path:** Absolute path, e.g., "/Users/takis/Zotero/storage/M3ALTMQZ/Chen_Wang_2023_VRP.pdf"
- **Abstract (optional):** First 150 characters, append "…" if longer

### 10. Handle Edge Cases

- **Collection not found:** List available collections and ask user to clarify
- **No results:** Show "No results found for '[query]' in [collection]. Try broader search terms or different collection."
- **Item with no PDF:** Show "No PDF" in PDF Path column
- **Missing authors:** Show "Unknown" in Authors column
- **Missing year:** Show "N/A" in Year column
- **Semantic search unavailable:** Silently fall back to collection-based search with note: "Using collection search (semantic search unavailable)"
- **Query too short:** Offer to enhance (e.g., "RL" might mean reinforcement learning, machine learning, etc.)

## Search Strategy Decision Tree

```
User provides query
├─ Query length >= 5 words AND not an acronym?
│  └─ Yes: Try semantic search first
│     ├─ Success: Return results
│     └─ Fail: Fall back to collection-based search
├─ Query < 5 words OR is an acronym?
│  └─ Offer enhancement: "Enhanced query: '[expanded]' — OK?"
│     ├─ User approves: Use enhanced query (repeat above)
│     └─ User rejects: Use original query with collection search
└─ User mentions tags explicitly?
   └─ Use tag search instead
```

## Query Enhancement Examples

| Original | Enhanced | Reason |
|----------|----------|--------|
| "RL" | "reinforcement learning Q-learning policy gradient" | Acronym expansion + related terms |
| "optimization" | "combinatorial optimization machine learning algorithms heuristics" | Generic → domain-specific |
| "agents" | "multi-agent systems agent architectures agent design patterns" | Vague → specific contexts |
| "GNN" | "graph neural networks graph convolution message passing" | Acronym + architecture details |
| "VRP" | "vehicle routing problem TSP combinatorial optimization" | Acronym + related problems |

## References

For detailed technical documentation, see:

- **Execution Guide:** `references/execution-guide.md` — Tool schemas, collection resolution, token cost analysis
- **Output Formats:** `references/output-formats.md` — Field specifications, missing data handling, alternative formats
- **Troubleshooting:** `references/troubleshooting.md` — Common errors, edge cases, debugging checklist

## Example Interactions

### Example 1: Basic Search (Default Parameters)

```
User: "Find papers about graph neural networks in logistics"

Execution:
1. Parse: query="graph neural networks in logistics", collection="Research", limit=10
2. Collection key cached (or looked up): L7DYN5N5
3. Semantic search for "graph neural networks in logistics" → 12 results
4. Fetch metadata for top 10
5. Fetch attachments for each

Output:
**Zotero Search: "graph neural networks in logistics"** | 10 results | Research

| # | Title | Authors | Year | Zotero ID | PDF Path |
|---|---|---|---|---|---|
| 1 | Combinatorial Optimization with Automated Graph Neural Networks | Liu, Y., Zhang, P., Wang, X. | 2024 | M3ALTMQZ | /Users/takis/Zotero/storage/M3ALTMQZ/Liu_et_al_2024_Combinatorial.pdf |
| 2 | Learning Neural Networks for Vehicle Routing | Chen, M., Wang, S. | 2023 | K7QWBXYZ | /Users/takis/Zotero/storage/K7QWBXYZ/Chen_Wang_2023_VRP.pdf |
```

### Example 2: Custom Collection and Limit

```
User: "Search Optimization collection for vehicle routing, show 5 results"

Execution:
1. Parse: query="vehicle routing", collection="Optimization", limit=5
2. Collection key lookup/cached: K2QWBXYZ
3. Semantic search → 8 results, take top 5
4. Fetch metadata + attachments

Output:
**Zotero Search: "vehicle routing"** | 5 results | Optimization

| # | Title | Authors | Year | Zotero ID | PDF Path |
|---|---|---|---|---|---|
| 1 | Optimal Routing Strategies for Fleet Optimization | Johnson, R., Davis, L. | 2023 | P9MNBVCX | /Users/takis/Zotero/storage/P9MNBVCX/Johnson_2023.pdf |
| 2 | ... | ... | ... | ... | ... |
```

### Example 3: Query Enhancement (Acronym)

```
User: "Find papers about RL"

Execution:
1. Parse: query="RL" (detected as acronym, <5 words)
2. Generate enhancement: "reinforcement learning deep Q-learning policy gradient actor-critic"
3. Ask user: "Enhanced query: 'reinforcement learning deep Q-learning policy gradient actor-critic' — OK?"
4. User approves
5. Semantic search with enhanced query → results

Output:
**Zotero Search: "reinforcement learning deep Q-learning policy gradient actor-critic"** | 10 results | Research
```

### Example 4: With Abstracts

```
User: "Find papers about agents, include abstracts"

Execution:
1. Parse: query="agents", include_abstract=true
2. Search → results
3. Fetch metadata WITH abstracts
4. Format output with abstract column

Output:
**Zotero Search: "agents" (with abstracts)** | 10 results | Research

| # | Title | Authors | Year | Abstract |
|---|---|---|---|---|
| 1 | Multi-Agent Reinforcement Learning Systems | Smith, J. | 2024 | This paper presents a comprehensive framework for training collaborative multi-agent systems… |
```

### Example 5: No Results

```
User: "Find papers about quantum computing in medieval history"

Execution:
1. Parse & search
2. Semantic search returns 0 results
3. Collection search also returns 0 results

Output:
No results found for "quantum computing in medieval history" in Research collection. Try:
- Broader search terms: "quantum computing" or "medieval history"
- Different collection: Try Papers or Optimization collections
- Tag search: Search by tags instead of keywords
```

### Example 6: Collection Not Found

```
User: "Search MyCollection for machine learning"

Execution:
1. Parse: collection="MyCollection"
2. Collection lookup fails (not found)
3. List available collections

Output:
Collection "MyCollection" not found. Available collections:
- Research (L7DYN5N5)
- Optimization (K2QWBXYZ)
- Papers (P9MNBVCX)
- Archive (Z3XYZABC)

Which collection would you like to search?
```

## Related Skills

**Other search skills:** `/search-web` · `/search-youtube` · `/search-perplexity`
