# Zotero Search — Troubleshooting Guide

## Overview

This guide covers common errors, debugging strategies, and edge cases when using the zotero-search skill. Use this when unexpected behavior occurs or results seem incomplete.

---

## Common Errors & Solutions

### 1. "Tool not found" / Zotero MCP Server Not Available

**Error Message:**
```
Tool not found: mcp__zotero__zotero_semantic_search
```

**Cause:** Zotero MCP server is not running or not available in Claude Code environment.

**Solutions:**

1. **Verify Zotero is running:**
   - Open Zotero desktop application (not browser extension)
   - Check that it's actively running (not minimized or closed)

2. **Check MCP server connection:**
   - Restart Claude Code and try again
   - If error persists, the Zotero MCP server may not be properly configured
   - Verify in Claude Code settings that Zotero MCP is enabled

3. **Fallback approach:**
   - If semantic search tool unavailable, skill automatically falls back to collection-based search
   - User should still get results, just possibly less relevant

4. **Manual workaround:**
   - Open Zotero directly and use its search feature
   - Or use a different collection explicitly: "search Optimization collection for [topic]"

---

### 2. Collection Not Found

**Error Output:**
```
Collection "MyCollection" not found. Available collections:
- Research (L7DYN5N5)
- Optimization (K2QWBXYZ)
```

**Cause:** User typed collection name incorrectly, or collection doesn't exist in library.

**Debugging:**
1. Check spelling (case-insensitive, but name must match)
2. Verify collection exists in Zotero (open Zotero → check left sidebar)
3. Note: Subcollections are shown with parent context (e.g., "Research > Logistics")

**Solution:**
1. User selects correct collection name from list provided
2. For subcollections: Use full path "Research > Logistics" or just the subcollection name "Logistics"
3. If using subcollection, ensure skill resolves it correctly (may need testing)

**Testing subcollections:**
```python
# When collection lookup fails with simple name, try parent > child
if collection_key is None and ">" not in collection_name:
    # Try matching as subcollection under common parents
    for coll in collections:
        if coll["parent_collection"] and coll["name"].lower() == collection_name.lower():
            return coll["key"]
```

---

### 3. No Results Found

**Error Output:**
```
No results found for "quantum cryptography in medieval times" in Research collection. Try:
- Broader search terms
- Different collection
```

**Common Causes:**

| Cause | Example | Solution |
|-------|---------|----------|
| Query too specific | "Transformer attention mechanism with bidirectional flow" | Use "transformer" or "attention" alone |
| Query uses niche terminology | "vehicular fog computing with 5G" | Try "fog computing" or "vehicular networks" |
| Topic not in collection | "medical imaging ML" searched in Optimization collection | Search Research collection instead |
| Typos or misspellings | "vehicel routing" | Correct spelling: "vehicle routing" |
| Date filter too restrictive | Old papers in broad area | Remove date restrictions |

**Debugging Steps:**

1. **Try broader query:**
   ```
   User: "Find papers about RL"
   Skill: "Enhanced query: 'reinforcement learning machine learning agents' — OK?"
   ```

2. **Check collection contents:**
   - Ask user: "What topics are in Research collection?"
   - Or show a sample of items in collection

3. **Try different search mode:**
   - If semantic search returns 0, try collection-based search
   - If collection search returns 0, try tag-based search

4. **Suggest alternatives:**
   ```
   "Try searching for:
   - Broader terms: 'learning' or 'networks'
   - Different collection: Optimization or Papers
   - By tags: Filter by subject tags instead
   ```

---

### 4. Semantic Search Unavailable / Returns No Results

**Error Behavior:**
```
[Silent fallback to collection-based search]
Using collection search (semantic search unavailable)
**Zotero Search: "[query]"** | N results | Research
```

**Cause:** Semantic search database not initialized, or embeddings not available.

**Debugging:**
```python
try:
    results = mcp__zotero__zotero_semantic_search(...)
except SemanticSearchUnavailableError:
    # Automatically fall back
    results = mcp__zotero__zotero_get_collection_items(...)
    # Notify user of fallback
```

**Solution:**
- Skill handles this automatically (no user action needed)
- Results are still returned, may be less precisely ranked
- If user wants better results, suggest:
  1. Try more specific terms
  2. Search a smaller, more focused collection
  3. Use tags (if available): "search by tags [subject]"

---

### 5. Missing PDF Attachments

**Output:**
```markdown
| 3 | Important Paper on Optimization | Garcia, L. | 2022 | K7QWERTY | No PDF |
```

**Cause:** Item exists in Zotero but has no PDF file attached.

**Debugging:**
```python
# Check attachment list
if not extract_pdf_info(children):
    # No PDF found
    return {"zotero_id": "N/A", "pdf_path": "No PDF"}
```

**Solutions:**
1. **For user:**
   - Open the item in Zotero
   - Manually attach the PDF (File → Add Attachment)
   - Or find online version (Retrieve metadata from DOI, etc.)

2. **For skill:**
   - Show "No PDF" in output (don't skip row)
   - Allow user to click on Zotero ID to open item in Zotero
   - Optionally provide DOI link if available

3. **Verify path is correct:**
   ```python
   pdf_path = "/Users/takis/Zotero/storage/K7QWERTY/filename.pdf"
   if not Path(pdf_path).exists():
       # File not found on disk (rare, indicates sync issue)
       return "No PDF (file missing on disk)"
   ```

---

### 6. Missing Authors

**Output:**
```markdown
| 2 | Handbook of Optimization | Unknown | 2021 | M3ASDFGH | /Users/.../handbook.pdf |
```

**Cause:** Zotero item has no author metadata (common for handbooks, reports, archival items).

**Debugging:**
```python
if not creators or len(creators) == 0:
    return "Unknown"
```

**Solution:**
- This is expected for some content types (handbooks, reports, archives)
- User can manually add author info in Zotero if desired
- Check publication title or other fields for context

---

### 7. Missing Year

**Output:**
```markdown
| 5 | Emerging Optimization Methods | Wilson, R., et al. | N/A | P2XYZWER | /Users/.../paper.pdf |
```

**Cause:** Zotero item has no publication year metadata.

**Common for:**
- Preprints (posted but not yet published)
- Theses or dissertations (may show "2023-02-15" but not full year extraction)
- Archival items without clear dates
- Web pages or blogs

**Solutions:**
- Accept "N/A" as valid (don't filter out the row)
- User can add date in Zotero if it's a known publication
- For sorting, treat "N/A" as oldest (sort to end of list)

---

### 8. Paths Not Opening / File Not Found

**Error:** User clicks PDF path but file doesn't open, or "File not found" error.

**Cause:** Zotero storage path incorrect, or file has been moved/deleted.

**Debugging:**
```python
from pathlib import Path

# Verify file exists before returning path
pdf_path = construct_pdf_path(attachment_key, filename)
if not Path(pdf_path).exists():
    return "No PDF (file missing)"
```

**Solutions:**

1. **Verify file exists:**
   ```bash
   ls -la /Users/takis/Zotero/storage/M3ALTMQZ/
   ```
   Should show the PDF file

2. **Check Zotero sync:**
   - Open Zotero
   - Go to Edit → Preferences → Sync
   - Verify storage location is correct
   - Run manual sync if needed

3. **For Windows/Linux users:**
   - Verify path separators are correct (\ vs /)
   - Check user's Zotero storage location (may not be in default)
   - Run: `echo $HOME` or `echo %USERPROFILE%` to verify home directory

4. **Filename encoding issues:**
   - Some filenames have special characters
   - If path has unicode, ensure proper encoding

---

### 9. Query Enhancement Not Working

**Scenario:** User provides vague query, but no enhancement offered.

**Debugging:**
```python
# Enhancement should trigger for:
if len(query.split()) < 5 or is_acronym(query) or is_generic(query):
    # Should offer enhancement
    enhanced = enhance_query(query)
    # Ask: "Enhanced query: '[enhanced]' — OK?"
```

**If enhancement not triggered:**

1. **Check query length:**
   - "reinforcement learning" = 2 words → should enhance
   - "deep Q-learning for robotics" = 4 words → should enhance
   - "multi-agent cooperative reinforcement learning systems" = 5 words → no enhancement

2. **Check acronym detection:**
   ```python
   def is_acronym(text: str) -> bool:
       return len(text) <= 4 and text.isupper()

   # Examples:
   is_acronym("RL")     # True
   is_acronym("GNN")    # True
   is_acronym("agents") # False
   ```

3. **Manual enhancement:**
   - User can always say "enhance this query" explicitly
   - Or specify enhanced terms themselves

---

### 10. Performance / Slow Searches

**Symptom:** Search takes very long time (>30 seconds).

**Cause:** Large library or slow semantic search indexing.

**Solutions:**

1. **For large libraries (1000+ items):**
   - Use collection-based search instead: "search Optimization collection"
   - Collections are faster than full library search
   - Semantic search can be slow on first run (indexing)

2. **Optimize query:**
   - More specific query → fewer results → faster
   - "reinforcement learning" is faster than "learning"

3. **Reduce limit:**
   - "Find 5 papers about X" faster than "Find 50 papers"
   - Default 10 results is balanced

4. **Check Zotero:**
   - Open Zotero directly
   - Check for sync/index operations in progress
   - If indexing, wait for completion before searching

---

## Edge Cases

### Subcollections (Nested Collections)

**Scenario:** User requests "search Research > Logistics collection"

**Handling:**
```python
# Collections can be nested (parent > child)
def resolve_collection(name: str, collections: list) -> str:
    if " > " in name:
        # Handle "Parent > Child" format
        parts = [p.strip() for p in name.split(">")]
        # Find child collection with matching parent
        for coll in collections:
            if coll["name"] == parts[-1]:  # Match last part
                # Verify parent if provided
                if len(parts) > 1:
                    parent_name = parts[0]
                    # Check parent matches (optional validation)
                return coll["key"]
    else:
        # Simple name lookup (should match regardless of parent)
        for coll in collections:
            if coll["name"].lower() == name.lower():
                return coll["key"]
```

### Multiple Authors with Same Last Name

**Example:**
```
"Smith, J., Smith, M., Johnson, R., et al."
```

**Handling:**
- Format as returned (first initial distinguishes)
- If two authors have same name and initial: "Smith, J." and "Smith, J." → Include both with possible differentiation
- Current format already handles this by truncating to first 3 authors

### Very Long Titles

**Example:**
```
"A Deep Reinforcement Learning Approach to Multi-Objective Optimization with Constraints in Non-Convex Solution Spaces: Applications to Vehicle Routing…"
```

**Handling:**
```python
def truncate_title(title: str, max_len: int = 80) -> str:
    if len(title) <= max_len:
        return title
    return title[:max_len - 1] + "…"
```

Result: Truncates at 80 chars, user can open PDF to see full title.

### Very Long PDF Path (Windows)

**Scenario:** Windows path exceeds 260 character limit (legacy limitation).

**Symptoms:** "Path too long" error when trying to open file.

**Solution:**
- Windows 10+: Enable long paths in registry (requires admin)
- Or: User can create symlink to Zotero storage folder with shorter path
- Skill can't control this, but should inform user if detected

---

## MCP Connection Troubleshooting

### Zotero MCP Server Not Responding

**Error:**
```
Error: Timeout waiting for Zotero MCP server response
```

**Debugging Checklist:**

- [ ] Zotero desktop application is open
- [ ] Zotero window is active (not minimized)
- [ ] Internet connection is working
- [ ] Zotero library is not currently syncing (check sync indicator)
- [ ] No error messages in Zotero interface
- [ ] Claude Code is configured with Zotero MCP enabled

**Recovery Steps:**

1. Close Claude Code
2. Close Zotero
3. Wait 5 seconds
4. Reopen Zotero
5. Reopen Claude Code
6. Try search again

### Authentication Issues

**Error:**
```
Error: Zotero authentication failed
```

**Cause:** Zotero MCP server requires valid Zotero session.

**Solution:**
- Zotero must be actively open (desktop app)
- Browser extension alone is not sufficient
- Verify user is logged into Zotero or using local library

---

## Debug Checklist

Use this checklist when troubleshooting unexpected behavior:

### For "No Results" Issues

- [ ] Query is not empty or just whitespace
- [ ] Query matches expected keywords (user can verify in Zotero)
- [ ] Collection name is correct
- [ ] Collection has items (user can check in Zotero)
- [ ] Semantic search is responding or falling back
- [ ] Collection filtering logic is matching query correctly

### For "Missing Data" Issues

- [ ] Zotero item has all required metadata (user can check)
- [ ] PDF attachment exists in Zotero
- [ ] Attachment is stored in expected path structure
- [ ] No special characters in filename breaking display
- [ ] Year/date field is populated (if expected)

### For "Slow Performance" Issues

- [ ] Library size (count items: View → Library Statistics)
- [ ] Semantic search index status (check Zotero settings)
- [ ] Network/internet connection speed
- [ ] Other processes consuming resources
- [ ] Zotero is not currently indexing or syncing

### For "Path Issues"

- [ ] Path format matches user's OS (/, \, C:\)
- [ ] Home directory expansion works (`~` → `/Users/takis`)
- [ ] Attachment key is valid (8 alphanumeric)
- [ ] Filename includes extension (e.g., `.pdf`)
- [ ] File actually exists on disk

---

## Reporting Issues

If you encounter an error not listed here:

1. **Collect information:**
   - Full error message (copy-paste)
   - Query that triggered error
   - Collection being searched
   - Number of items in library (approx)
   - OS and platform (macOS/Linux/Windows)

2. **Try to reproduce:**
   - Run the same search again
   - Try with different query
   - Try with different collection
   - Check if Zotero is still running

3. **Check Zotero directly:**
   - Open Zotero
   - Try the search manually
   - Verify item metadata
   - Check if PDF attachments exist

4. **Check Claude Code:**
   - Verify Zotero MCP is enabled
   - Try restarting Claude Code
   - Check if other MCP tools work

---

## Performance Benchmarks

Expected performance for typical operations:

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Collection lookup (first) | <1s | Cached after first use |
| Collection lookup (cached) | <0.1s | No API call |
| Semantic search (10 results) | 2-5s | Depends on index size |
| Collection search (10 results) | 1-3s | Faster than semantic |
| Fetch metadata (10 items) | 2-4s | Parallel calls |
| Fetch attachments (10 items) | 2-4s | Parallel calls |
| **Total first search** | 6-12s | Includes all steps |
| **Total cached search** | 5-11s | Collection key cached |

For very large libraries (5000+ items), add 50-100% overhead.

---

## Token Usage Troubleshooting

### High Token Usage

**If searches are using more tokens than expected (>1000):**

1. **Check abstracts:**
   - Are abstracts being included? (Should not by default)
   - Abstracts add 200-300 tokens per result

2. **Check preamble:**
   - Skill should have no preamble text
   - Only: "**Zotero Search: ...**" header + table

3. **Check result count:**
   - Asking for 50 results uses more tokens than 10
   - Metadata + formatting scales with result count

4. **Optimize:**
   - Reduce limit: "Find 5 papers instead of 20"
   - Disable abstracts: Omit "include abstracts"
   - Use more specific query: Fewer results = fewer tokens

---

## When to Contact Support

Contact the Claude Code team if:

- Zotero MCP server consistently unavailable
- Cannot construct valid PDF paths
- Security/authentication errors
- Persistent database errors from Zotero
- Performance extremely slow (>60s per search)
- Reproducible crashes in skill execution

Otherwise, check this troubleshooting guide and try alternative approaches listed in solutions.
