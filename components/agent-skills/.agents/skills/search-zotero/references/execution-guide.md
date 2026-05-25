# Zotero Search — Execution Guide

## Overview

This guide provides detailed technical documentation for implementing the zotero-search skill. It covers tool schemas, collection resolution algorithms, search strategies, token optimization, and cross-platform path handling.

---

## Zotero MCP Tool Schemas

### 1. mcp__zotero__zotero_get_collections

**Purpose:** List all collections in the user's Zotero library.

**Input Schema:**
```python
{
    "limit": int | str | null  # Optional, max results to return (default: None = all)
}
```

**Output Schema:**
```python
{
    "successful": bool,
    "collections": [
        {
            "key": str,              # Collection ID (e.g., "L7DYN5N5")
            "name": str,             # Display name (e.g., "Research")
            "numItems": int,         # Number of items in collection
            "parent_collection": str | null,  # Parent key if subcollection
            "level": int             # Nesting level (0 = top-level)
        },
        ...
    ]
}
```

**Example Response:**
```json
{
    "successful": true,
    "collections": [
        {
            "key": "L7DYN5N5",
            "name": "Research",
            "numItems": 487,
            "parent_collection": null,
            "level": 0
        },
        {
            "key": "K2QWBXYZ",
            "name": "Optimization",
            "numItems": 156,
            "parent_collection": null,
            "level": 0
        },
        {
            "key": "M5VBNMOP",
            "name": "Logistics",
            "numItems": 89,
            "parent_collection": "L7DYN5N5",
            "level": 1
        }
    ]
}
```

**Collection Resolution Algorithm:**

```python
def resolve_collection(user_collection_name: str, collections: list) -> str:
    """
    Find collection by name (case-insensitive) and return its key.

    Args:
        user_collection_name: Name provided by user (e.g., "Research")
        collections: List of collection dicts from zotero_get_collections

    Returns:
        Collection key (e.g., "L7DYN5N5")

    Raises:
        ValueError: If collection not found
    """
    normalized_user_name = user_collection_name.lower().strip()

    for coll in collections:
        if coll["name"].lower().strip() == normalized_user_name:
            return coll["key"]

    # Not found
    raise ValueError(f"Collection '{user_collection_name}' not found")


def list_available_collections(collections: list) -> str:
    """Format available collections for user display."""
    top_level = [c for c in collections if c["level"] == 0]
    return "\n".join(f"- {c['name']} ({c['key']})" for c in top_level)
```

---

### 2. mcp__zotero__zotero_semantic_search

**Purpose:** AI-powered semantic search over Zotero library using embeddings.

**Input Schema:**
```python
{
    "query": str,                          # Search query (required)
    "limit": int | str | null,            # Max results (default: 10, max: 100)
    "filters": dict | null  # Optional filters
    # filters can include:
    # - "created_date_range": {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
    # - "tags": ["tag1", "tag2"]  # AND logic
}
```

**Output Schema:**
```python
{
    "successful": bool,
    "query": str,
    "results_count": int,
    "items": [
        {
            "key": str,                    # Item key (e.g., "ABCD1234")
            "title": str,
            "creators": [
                {
                    "firstName": str,
                    "lastName": str,
                    "creatorType": str     # "author", "editor", etc.
                },
                ...
            ],
            "date": str,                   # Publication date (often just year)
            "itemType": str,               # "journalArticle", "book", etc.
            "publicationTitle": str | null,
            "relevance_score": float       # 0-1, higher = more relevant (for sorting)
        },
        ...
    ]
}
```

**Example Call:**
```python
mcp__zotero__zotero_semantic_search
arguments={
    "query": "graph neural networks in logistics",
    "limit": 10
}
```

**Token Cost:** ~2 API calls + embedding computation. Efficient for natural language queries.

---

### 3. mcp__zotero__zotero_get_collection_items

**Purpose:** Get all items in a specific collection (fallback for when semantic search unavailable).

**Input Schema:**
```python
{
    "collection_key": str,    # Collection ID (from zotero_get_collections)
    "limit": int | str | null # Max items (default: 50)
}
```

**Output Schema:**
```python
{
    "successful": bool,
    "collection_key": str,
    "collection_name": str,
    "items_count": int,
    "items": [
        {
            "key": str,
            "title": str,
            "creators": [...],
            "date": str,
            "itemType": str
        },
        ...
    ]
}
```

**Usage Notes:**
- Returns items in default order (usually most recent first)
- For filtering: Extract query terms and match against title/creators locally
- Inline filtering formula:
  ```python
  def filter_by_query(items: list, query: str, limit: int) -> list:
      """Filter items by query match in title or creators."""
      query_terms = query.lower().split()
      scored = []

      for item in items:
          title = item.get("title", "").lower()
          authors = " ".join(
              f"{c.get('firstName', '')} {c.get('lastName', '')}".lower()
              for c in item.get("creators", [])
          )

          # Count term matches
          matches = sum(
              title.count(term) + authors.count(term)
              for term in query_terms
          )

          if matches > 0:
              scored.append((item, matches))

      # Sort by match count (descending) then return top N
      scored.sort(key=lambda x: x[1], reverse=True)
      return [item for item, _ in scored[:limit]]
  ```

**Token Cost:** ~1 API call (collection lookup). Efficient for collection-based filtering.

---

### 4. mcp__zotero__zotero_get_item_metadata

**Purpose:** Fetch full metadata for a specific item.

**Input Schema:**
```python
{
    "item_key": str,               # Item key (from search results)
    "format": str | null,          # "markdown" (default) or "bibtex"
    "include_abstract": bool        # Default: false (faster)
}
```

**Output Schema:**
```python
{
    "successful": bool,
    "item_key": str,
    "title": str,
    "creators": [
        {
            "firstName": str,
            "lastName": str,
            "creatorType": str
        },
        ...
    ],
    "date": str | null,            # May be year-only (e.g., "2024") or full date
    "itemType": str,
    "publicationTitle": str | null,
    "volume": str | null,
    "issue": str | null,
    "pages": str | null,
    "DOI": str | null,
    "URL": str | null,
    "abstract": str | null,        # Only if include_abstract=true
    "notes": str | null,
    "tags": [str, ...] | null
}
```

**Example Call:**
```python
mcp__zotero__zotero_get_item_metadata
arguments={
    "item_key": "ABCD1234",
    "include_abstract": false,
    "format": "markdown"
}
```

**Year Extraction:**
```python
def extract_year(date_str: str | None) -> str:
    """Extract 4-digit year from date string."""
    if not date_str:
        return "N/A"

    # Try regex for 4-digit year
    import re
    match = re.search(r'\d{4}', date_str)
    return match.group(0) if match else "N/A"
```

**Token Cost:** ~1 API call per item. Parallelize for multiple items.

---

### 5. mcp__zotero__zotero_get_item_children

**Purpose:** Get child items (attachments, notes) for an item.

**Input Schema:**
```python
{
    "item_key": str  # Parent item key
}
```

**Output Schema:**
```python
{
    "successful": bool,
    "item_key": str,
    "children": [
        {
            "key": str,              # Attachment key (e.g., "M3ALTMQZ")
            "itemType": str,         # "attachment", "note"
            "title": str,            # Filename or note title
            "contentType": str | null,  # "application/pdf", "text/plain", etc.
            "tags": [str, ...] | null
        },
        ...
    ]
}
```

**Example Response:**
```json
{
    "successful": true,
    "item_key": "ABCD1234",
    "children": [
        {
            "key": "M3ALTMQZ",
            "itemType": "attachment",
            "title": "Liu_et_al_2024_Combinatorial_Optimization.pdf",
            "contentType": "application/pdf",
            "tags": []
        },
        {
            "key": "N5QWERTY",
            "itemType": "note",
            "title": "Summary notes",
            "contentType": null,
            "tags": []
        }
    ]
}
```

**PDF Extraction Logic:**
```python
def extract_pdf_info(children: list) -> tuple[str, str] | None:
    """
    Extract PDF attachment key and filename.

    Returns:
        (attachment_key, filename) if PDF found, None otherwise
    """
    for child in children:
        if (child.get("itemType") == "attachment" and
            child.get("contentType") == "application/pdf"):
            return (child["key"], child["title"])

    return None
```

**Token Cost:** ~1 API call per item. Parallelize for multiple items.

---

## PDF Path Construction

### Cross-Platform Path Format

The Zotero storage directory follows a consistent structure:

```
{ZOTERO_HOME}/storage/{ATTACHMENT_KEY}/{FILENAME}
```

**Platform-specific home directories:**

| Platform | Home Path |
|----------|-----------|
| macOS | `/Users/{username}/Zotero/storage/` |
| Linux | `/home/{username}/Zotero/storage/` |
| Windows | `C:\Users\{username}\Zotero\storage\` |

**Python helper:**
```python
import os
from pathlib import Path

def construct_pdf_path(attachment_key: str, filename: str) -> str:
    """
    Construct absolute PDF path using cross-platform home directory.

    Args:
        attachment_key: Zotero attachment key (e.g., "M3ALTMQZ")
        filename: Original filename from Zotero

    Returns:
        Absolute path (e.g., "/Users/takis/Zotero/storage/M3ALTMQZ/file.pdf")
    """
    zotero_home = Path.home() / "Zotero" / "storage" / attachment_key / filename
    return str(zotero_home)


def construct_pdf_path_windows(attachment_key: str, filename: str) -> str:
    """Windows-specific version (for reference)."""
    # On Windows, use backslashes
    return f"C:\\Users\\{os.getenv('USERNAME')}\\Zotero\\storage\\{attachment_key}\\{filename}"
```

### Path Verification

On macOS (where user is):
```python
def verify_pdf_exists(pdf_path: str) -> bool:
    """Check if PDF file actually exists."""
    return Path(pdf_path).exists()
```

---

## Search Strategy Decision Tree

```
User provides query
│
├─ Is query >= 5 words AND not an acronym?
│  │
│  └─ YES: Try semantic search
│     ├─ Success & results > 0?
│     │  └─ YES: Return ranked results
│     │
│     └─ Fail or empty?
│        └─ Fall back to collection-based search with inline filtering
│
├─ Is query < 5 words OR is an acronym?
│  │
│  └─ YES: Offer enhancement
│     ├─ User approves enhancement?
│     │  └─ YES: Use enhanced query, try semantic search
│     │
│     └─ User rejects or ignores?
│        └─ Use collection-based search with original query
│
└─ Did user mention tags explicitly?
   │
   └─ YES: Use tag-based search (semantic_search with tags filter)
```

### Implementation Pattern

```python
async def search_zotero(query: str, limit: int = 10, collection_key: str = None) -> list:
    """
    Execute search strategy.

    Returns:
        List of dicts with keys: title, creators, date, zotero_id (attachment key), pdf_path
    """

    # Step 1: Determine if enhancement needed
    if len(query.split()) < 5 or is_acronym(query):
        enhanced = enhance_query(query)
        # Ask user (would be AskUserQuestion in Claude Code)
        # For now, assume user approves
        search_query = enhanced
    else:
        search_query = query

    # Step 2: Try semantic search
    try:
        results = await semantic_search(search_query, limit)
        if results and len(results) > 0:
            return format_results(results)
    except Exception as e:
        print(f"Semantic search failed: {e}")

    # Step 3: Fall back to collection-based search
    if collection_key:
        items = await get_collection_items(collection_key, limit * 2)
        filtered = filter_by_query(items, query, limit)
        return format_results(filtered)

    # Step 4: No results
    return []
```

---

## Token Cost Analysis

### Typical Search Workflow

Scenario: User searches for "graph neural networks in logistics" with defaults (Research collection, 10 results)

| Step | Tool | Calls | Cost | Notes |
|------|------|-------|------|-------|
| 1 | Collection lookup | 1 (cached after first) | Low | ~1 API call, cached in session |
| 2 | Semantic search | 1 | Medium | ~2 API calls (search + embeddings) |
| 3 | Fetch metadata | 10 | Medium | 10 parallel calls (1 each) |
| 4 | Fetch attachments | 10 | Low | 10 parallel calls (1 each) |
| **Total** | | 21 (first run) | | **~5 tool calls/requests** |
| **Total (subsequent)** | | 20 (cached collection) | | **~4 tool calls/requests** |

**Token cost per search:** ~400-600 tokens (metadata, formatting, overhead)

### Optimization Strategies

1. **Cache collection key** — Save "Research" → "L7DYN5N5" mapping in conversation memory
2. **Parallelize metadata/attachment fetches** — Fetch multiple items simultaneously
3. **Skip abstracts by default** — Only include if explicitly requested (`include_abstract=true`)
4. **Inline filtering** — Don't use workbench for <20 results
5. **No preamble text** — Jump straight to results

### Token Budget Examples

| Scenario | Calls | Tokens |
|----------|-------|--------|
| Basic search (10 results, no abstract) | 4 | ~450 |
| Search with abstracts (10 results) | 4 | ~700 |
| Large search (50 results, no abstract) | 4 | ~1200 |
| Multi-search session (4 searches, cached) | 16 | ~2000 |

---

## Batch Processing for Large Libraries

For libraries with 1000+ items:

### Strategy 1: Limit + Pagination

```python
def batch_search(query: str, limit: int = 10, page_size: int = 50):
    """
    For collection-based search with large results.

    Fetch page_size items, filter, return top limit results.
    """
    items = get_collection_items(limit=page_size)
    filtered = filter_by_query(items, query, limit)

    if len(filtered) < limit:
        # Optionally fetch next page
        items_page_2 = get_collection_items(limit=page_size, offset=page_size)
        more = filter_by_query(items_page_2, query, limit - len(filtered))
        filtered.extend(more)

    return filtered
```

### Strategy 2: Semantic Search (Recommended)

Semantic search handles large libraries better (ranked by relevance, not raw results).

---

## Caching Strategy

### Session-Level Caching

Store in conversation memory after first lookup:

```python
memory = {
    "zotero": [
        "Research collection key is L7DYN5N5",
        "Optimization collection key is K2QWBXYZ",
        "Home directory for paths: /Users/takis"
    ]
}
```

**Retrieve in subsequent calls:**
```python
def get_cached_collection_key(collection_name: str, memory: dict) -> str | None:
    """Extract cached collection key from memory."""
    for item in memory.get("zotero", []):
        if collection_name in item:
            # Parse "Research collection key is L7DYN5N5"
            return item.split("is ")[-1].strip()
    return None
```

---

## Error Handling

### Common Errors and Recovery

| Error | Cause | Recovery |
|-------|-------|----------|
| Collection not found | User typed wrong name | List available collections, ask for clarification |
| Semantic search unavailable | Database not initialized | Silently fall back to collection-based search |
| No results | Query too specific or library empty | Suggest broader terms or different collection |
| Missing PDF | Item has no attachment | Show "No PDF" in output, don't fail |
| MCP timeout | Server slow or disconnected | Show "Zotero server unavailable", suggest retry |

### Implementation Pattern

```python
try:
    results = semantic_search(query, limit)
except SemanticSearchUnavailableError:
    # Silent fallback
    results = collection_search(query, collection_key, limit)
except Exception as e:
    # Unexpected error
    raise UserFacingError(f"Search failed: {str(e)}")
```

---

## Cross-Platform Testing Checklist

- [ ] macOS: Path format `/Users/{user}/Zotero/storage/`
- [ ] Linux: Path format `/home/{user}/Zotero/storage/`
- [ ] Windows: Path format `C:\Users\{user}\Zotero\storage\`
- [ ] Collection names are case-insensitive
- [ ] Subcollections are handled (parent_collection field)
- [ ] PDF files open with system default viewer
