# Zotero Search — Output Formats

## Overview

This document specifies the format for zotero-search output across different scenarios. All outputs are designed for readability, token efficiency, and direct usability (especially PDF paths for file access).

---

## Default Output Format (Markdown Table)

### Structure

```markdown
**Zotero Search: "[query]"** | N results | [Collection name]

| # | Title | Authors | Year | Zotero ID | PDF Path |
|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... | ... |
```

### Column Specifications

#### # (Index)
- **Type:** Integer
- **Format:** 1-indexed sequence
- **Example:** `1`, `2`, `3`
- **Rules:**
  - Always starts at 1
  - Increments by 1 for each row
  - Left-aligned in table

#### Title
- **Type:** String
- **Format:** Full title, max 80 characters
- **Rules:**
  - Truncate at 80 characters if longer
  - Append "…" if truncated
  - Preserve important words (e.g., don't truncate acronyms)
  - Example: `"Combinatorial Optimization with Automated Graph Neural Networks for…"`
- **Missing data:** Show "[No Title]"

**Title truncation logic:**
```python
def truncate_title(title: str, max_len: int = 80) -> str:
    if len(title) <= max_len:
        return title
    return title[:max_len - 1] + "…"
```

#### Authors
- **Type:** String (comma-separated author list)
- **Format:** `"Last, F., Last2, F., Last3, F., et al."` for 4+ authors; `"Last, F., Last2, F."` for 2 authors; `"Last, F."` for 1 author
- **Rules:**
  - Format each author as "Last, FirstInitial"
  - Limit to first 3 authors
  - If more than 3 authors, append "et al."
  - Separate authors with comma and space
  - Sort by author order in original metadata
- **Missing data:** Show "Unknown"

**Authors formatting logic:**
```python
def format_authors(creators: list, max_authors: int = 3) -> str:
    """
    Format creators into "Last, F., Last2, F., et al." format.

    Args:
        creators: List of dicts with firstName, lastName, creatorType

    Returns:
        Formatted author string
    """
    if not creators:
        return "Unknown"

    authors = []
    for creator in creators:
        if creator.get("creatorType") != "author":
            continue  # Skip editors, translators, etc. (optional: include them)

        first_name = creator.get("firstName", "").strip()
        last_name = creator.get("lastName", "").strip()

        if not last_name:
            continue

        # Get first initial
        first_initial = first_name[0].upper() if first_name else "?"

        authors.append(f"{last_name}, {first_initial}")

    if not authors:
        return "Unknown"

    if len(authors) > max_authors:
        return ", ".join(authors[:max_authors]) + ", et al."
    else:
        return ", ".join(authors)
```

**Examples:**
- 1 author: `"Liu, Y."`
- 2 authors: `"Liu, Y., Zhang, P."`
- 3 authors: `"Liu, Y., Zhang, P., Wang, X."`
- 4+ authors: `"Liu, Y., Zhang, P., Wang, X., et al."`
- Missing authors: `"Unknown"`

#### Year
- **Type:** Integer (4-digit)
- **Format:** `"2024"`, `"2023"`, etc.
- **Rules:**
  - Extract year from date string (first 4 digits)
  - If year cannot be extracted, show "N/A"
  - Always 4 digits (e.g., "2024" not "24")
- **Missing data:** Show "N/A"

**Year extraction logic:**
```python
import re

def extract_year(date_str: str | None) -> str:
    """Extract 4-digit year from date string."""
    if not date_str:
        return "N/A"

    # Try to find 4-digit year
    match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
    return match.group(1) if match else "N/A"
```

#### Zotero ID
- **Type:** String
- **Format:** Attachment key (e.g., `"M3ALTMQZ"`)
- **Rules:**
  - This is the attachment key from `zotero_get_item_children`
  - Typically 8 alphanumeric characters
  - Used in path construction: `/Users/takis/Zotero/storage/{ZOTERO_ID}/{filename}`
  - Unique identifier for the PDF attachment
- **Missing data:** Show "No PDF" (if item has no attachment)

**Note:** This is NOT the item key; it's the attachment/storage key specifically.

#### PDF Path
- **Type:** String (absolute path)
- **Format:** `/Users/takis/Zotero/storage/{ZOTERO_ID}/{filename}` (macOS example)
- **Rules:**
  - Absolute path (starts with `/`, `C:\`, etc.)
  - Cross-platform: Use `Path.home()` to construct
  - Include full filename exactly as stored in Zotero
  - Path should be clickable/openable on user's system
- **Missing data:** Show "No PDF"

**Path construction:**
```python
from pathlib import Path

def construct_pdf_path(attachment_key: str, filename: str) -> str:
    """Construct absolute PDF path."""
    zotero_home = Path.home() / "Zotero" / "storage" / attachment_key / filename
    return str(zotero_home)
```

**Examples:**
- macOS: `/Users/takis/Zotero/storage/M3ALTMQZ/Liu_2024_Combinatorial.pdf`
- Linux: `/home/user/Zotero/storage/M3ALTMQZ/Liu_2024_Combinatorial.pdf`
- Windows: `C:\Users\user\Zotero\storage\M3ALTMQZ\Liu_2024_Combinatorial.pdf`

---

## Example: Default Output (10 Results, No Abstracts)

```markdown
**Zotero Search: "graph neural networks in logistics"** | 10 results | Research

| # | Title | Authors | Year | Zotero ID | PDF Path |
|---|---|---|---|---|---|
| 1 | Combinatorial Optimization with Automated Graph Neural Networks | Liu, Y., Zhang, P., Wang, X., et al. | 2024 | M3ALTMQZ | /Users/takis/Zotero/storage/M3ALTMQZ/Liu_et_al_2024_Combinatorial.pdf |
| 2 | Learning Neural Networks for Vehicle Routing Problems | Chen, M., Wang, S. | 2023 | K7QWBXYZ | /Users/takis/Zotero/storage/K7QWBXYZ/Chen_Wang_2023_VRP.pdf |
| 3 | Graph-Based Optimization for Supply Chain Networks | Johnson, R. | 2023 | P9MNBVCX | /Users/takis/Zotero/storage/P9MNBVCX/Johnson_2023_Supply_Chain.pdf |
| 4 | Deep Learning for Logistics and Route Planning | Martinez, L., Rodriguez, J., et al. | 2022 | X2ZQWERT | /Users/takis/Zotero/storage/X2ZQWERT/Martinez_Rodriguez_2022.pdf |
| 5 | Neural Network Applications in Transportation | Park, S., Lee, J. | 2022 | A5SDFGHJ | /Users/takis/Zotero/storage/A5SDFGHJ/Park_Lee_2022_Transportation.pdf |
| 6 | Optimization Algorithms for Logistics Networks | Thompson, D. | 2021 | Q2WERTYU | /Users/takis/Zotero/storage/Q2WERTYU/Thompson_2021_Optimization.pdf |
| 7 | Multi-Agent Systems for Supply Chain Optimization | Kumar, A., Singh, R., et al. | 2021 | W9XCVBNM | /Users/takis/Zotero/storage/W9XCVBNM/Kumar_Singh_2021_MultiAgent.pdf |
| 8 | Machine Learning for Freight Route Planning | Patel, V. | 2020 | E1ASDFGH | /Users/takis/Zotero/storage/E1ASDFGH/Patel_2020_Freight.pdf |
| 9 | Graph Neural Networks: A Survey | Chen, X., Li, Y., Zhang, Z., et al. | 2020 | R3DFGHJK | /Users/takis/Zotero/storage/R3DFGHJK/Chen_et_al_2020_Survey.pdf |
| 10 | Combinatorial Optimization Using Machine Learning | Smith, J., Brown, A. | 2019 | T5ZXCVBN | /Users/takis/Zotero/storage/T5ZXCVBN/Smith_Brown_2019_ML.pdf |
```

---

## With Abstracts Output

### Usage

When user requests "with abstracts" or `include_abstract=true`:

```markdown
**Zotero Search: "[query]" (with abstracts)** | N results | [Collection name]

| # | Title | Authors | Year | Abstract |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |
```

### Abstract Column Specification

- **Type:** String (excerpt)
- **Format:** First 150 characters of abstract
- **Rules:**
  - Truncate at 150 characters
  - Append "…" if truncated
  - Remove line breaks (replace with space)
  - Preserve complete sentences where possible
- **Missing data:** Show "[No abstract available]"

**Abstract formatting logic:**
```python
def format_abstract(abstract: str | None, max_len: int = 150) -> str:
    """Format abstract excerpt."""
    if not abstract:
        return "[No abstract available]"

    # Remove line breaks
    cleaned = abstract.replace("\n", " ").replace("\r", " ")

    # Replace multiple spaces with single space
    cleaned = " ".join(cleaned.split())

    if len(cleaned) <= max_len:
        return cleaned

    # Truncate at word boundary if possible
    truncated = cleaned[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len - 20:  # Don't truncate too early
        truncated = cleaned[:last_space]

    return truncated + "…"
```

### Example: With Abstracts (5 Results)

```markdown
**Zotero Search: "reinforcement learning" (with abstracts)** | 5 results | Research

| # | Title | Authors | Year | Abstract |
|---|---|---|---|---|
| 1 | Deep Reinforcement Learning for Robotic Control | Smith, J., Jones, A., et al. | 2024 | This paper presents a novel deep reinforcement learning framework for controlling multi-joint robotic systems. We demonstrate state-of-the-art performance on benchmark tasks… |
| 2 | A Survey of Multi-Agent Reinforcement Learning | Lee, S., Park, M. | 2023 | Multi-agent reinforcement learning (MARL) is an important research area for distributed decision-making. This survey reviews recent advances in cooperative and competitive… |
| 3 | Q-Learning Convergence Analysis | Chen, Y. | 2022 | We provide theoretical analysis of Q-learning convergence rates under various conditions. Novel bounds are derived for discount factors and learning rates that improve… |
| 4 | Policy Gradient Methods: A Comprehensive Review | Kumar, R., Singh, P., et al. | 2021 | Policy gradient methods form a core class of reinforcement learning algorithms. This comprehensive review covers actor-critic methods, trust region policies, and… |
| 5 | Efficient Exploration in Reinforcement Learning | Brown, T. | 2020 | Exploration remains a fundamental challenge in reinforcement learning. We propose a novel exploration strategy based on information-theoretic principles that balances… |
```

---

## Edge Cases & Missing Data

### Missing PDF Attachment

**Scenario:** Item exists but has no PDF attachment.

**Output:**
```markdown
| 5 | Optimization for Supply Chains | Garcia, L., Lopez, M. | 2022 | M9QWERTY | No PDF |
```

**Rules:**
- Show "No PDF" in the PDF Path column
- Include all other information normally
- Don't skip the row

### Missing Authors

**Scenario:** Item has no author information.

**Output:**
```markdown
| 3 | Advanced Logistics Handbook | Unknown | 2021 | K7ASDFGH | /Users/takis/Zotero/storage/K7ASDFGH/Handbook_2021.pdf |
```

**Rules:**
- Show "Unknown" in Authors column
- Continue with other fields normally

### Missing Year

**Scenario:** Item has no publication date.

**Output:**
```markdown
| 7 | Emerging Topics in Optimization | Wilson, R. | N/A | P2ZXCVBN | /Users/takis/Zotero/storage/P2ZXCVBN/Wilson_Emerging.pdf |
```

**Rules:**
- Show "N/A" in Year column
- This is common for preprints, theses, or archival items

### Missing Title

**Scenario:** Zotero item has no title (very rare).

**Output:**
```markdown
| 2 | [No Title] | Smith, J., et al. | 2023 | X9QWERTY | /Users/takis/Zotero/storage/X9QWERTY/attachment.pdf |
```

**Rules:**
- Show "[No Title]" in Title column
- Continue with other fields

### Collection Not Found

**Scenario:** User requests search in non-existent collection.

**Output:**
```
Collection "MyPapers" not found. Available collections:
- Research (L7DYN5N5)
- Optimization (K2QWBXYZ)
- Logistics (M5VBNMOP)
- Archive (Z3XYZABC)

Which collection would you like to search?
```

### No Results

**Scenario:** Search returns 0 results.

**Output:**
```
No results found for "quantum cryptography in medieval times" in Research collection. Try:
- Broader search terms: "quantum cryptography" or "medieval history"
- Different collection: Try Papers or Archive collections
- Tag-based search: Filter by tags instead of keywords
```

---

## Alternative Output Formats (Future)

While the default is Markdown table, the skill can support these formats with user request:

### JSON Format

**Usage:** "Show results as JSON" or "JSON format"

```json
{
  "query": "graph neural networks",
  "collection": "Research",
  "result_count": 3,
  "results": [
    {
      "index": 1,
      "title": "Combinatorial Optimization with Automated Graph Neural Networks",
      "authors": [
        {"firstName": "Y", "lastName": "Liu"},
        {"firstName": "P", "lastName": "Zhang"}
      ],
      "year": 2024,
      "zotero_id": "M3ALTMQZ",
      "pdf_path": "/Users/takis/Zotero/storage/M3ALTMQZ/Liu_et_al_2024.pdf",
      "abstract": null
    }
  ]
}
```

### CSV Format

**Usage:** "Show as CSV" or "CSV export"

```csv
Index,Title,Authors,Year,Zotero ID,PDF Path
1,Combinatorial Optimization with Automated Graph Neural Networks,"Liu, Y., Zhang, P., et al.",2024,M3ALTMQZ,/Users/takis/Zotero/storage/M3ALTMQZ/Liu_et_al_2024.pdf
2,Learning Neural Networks for Vehicle Routing Problems,"Chen, M., Wang, S.",2023,K7QWBXYZ,/Users/takis/Zotero/storage/K7QWBXYZ/Chen_Wang_2023_VRP.pdf
```

### List Format

**Usage:** "Show as list" or "list format"

```
**Zotero Search: "graph neural networks in logistics"** | 10 results | Research

1. **Combinatorial Optimization with Automated Graph Neural Networks**
   Authors: Liu, Y., Zhang, P., Wang, X., et al.
   Year: 2024
   Zotero ID: M3ALTMQZ
   PDF: /Users/takis/Zotero/storage/M3ALTMQZ/Liu_et_al_2024.pdf

2. **Learning Neural Networks for Vehicle Routing Problems**
   Authors: Chen, M., Wang, S.
   Year: 2023
   Zotero ID: K7QWBXYZ
   PDF: /Users/takis/Zotero/storage/K7QWBXYZ/Chen_Wang_2023_VRP.pdf
```

---

## Sorting & Ranking

### Default Ordering

**Semantic search:** Ranked by relevance score (descending)
- Items most relevant to query appear first
- Relevance determined by semantic embedding similarity

**Collection-based search:** Ranked by match count (descending)
- Items matching more query terms appear first
- Ties broken by most recent year first

### Optional Sorting

**If user requests:** "Sort by year" or "most recent first"

```markdown
| # | Title | Authors | Year | Zotero ID | PDF Path |
|---|---|---|---|---|---|
| 1 | ... | ... | 2024 | ... | ... |
| 2 | ... | ... | 2023 | ... | ... |
| 3 | ... | ... | 2022 | ... | ... |
```

---

## Token-Efficient Output Tips

1. **No preamble** — Omit "Here are the results" or "I found..."
2. **Single summary line** — `**Zotero Search: "[query]"** | N results | [Collection]`
3. **Compact table** — Only essential columns, no extra formatting
4. **Inline data** — Don't use workbench for <20 results
5. **Truncate titles** — 80 chars max keeps table readable
6. **No commentary** — Return results only unless asked to analyze

---

## Verification Checklist

- [ ] All 6 columns present: #, Title, Authors, Year, Zotero ID, PDF Path
- [ ] Title truncated at 80 characters with "…"
- [ ] Authors formatted as "Last, F., Last2, F., et al."
- [ ] Year is 4 digits or "N/A"
- [ ] Zotero ID is attachment key (8 alphanumeric)
- [ ] PDF Path is absolute, uses `Path.home()` for cross-platform
- [ ] Missing data shown as "Unknown", "N/A", or "No PDF"
- [ ] Summary line: `**Zotero Search: "[query]"** | N results | [Collection]`
- [ ] No preamble text
- [ ] Table is readable and properly aligned
