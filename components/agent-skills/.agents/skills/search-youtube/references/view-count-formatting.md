# View Count Formatting Reference

## Compact Number Formatting Rules

Apply these rules when formatting view counts in output:

### Formatting Table

| Raw Count | Formatted | Example |
|---|---|---|
| 0–999 | As-is, no suffix | 890 |
| 1,000–9,999 | X.XK (one decimal) | 5.2K |
| 10,000–99,999 | XXK (no decimal) | 45K |
| 100,000–999,999 | XXXK (no decimal) | 350K |
| 1,000,000–9,999,999 | X.XM (one decimal) | 1.2M |
| 10,000,000–99,999,999 | XXM (no decimal) | 25M |
| 100,000,000–999,999,999 | XXXM (no decimal) | 450M |
| 1,000,000,000+ | X.XB (one decimal) | 1.1B |

### Rules

1. **One decimal place** for values under 10 in their unit
   - ✓ 1.2M, 5.7K
   - ✗ 1M, 5K (missing decimal)
   - ✗ 1.23M, 5.67K (too many decimals)

2. **No decimal** for values 10+ in their unit
   - ✓ 35K, 150M, 2.5B
   - ✗ 35.0K, 150.0M (unnecessary decimals)

3. **Never show raw numbers** with commas in output
   - ✗ "1,200,000 views"
   - ✓ "1.2M views"

4. **No spaces** between number and suffix
   - ✓ "1.2M"
   - ✗ "1.2 M"

## Implementation Examples

### Python Function

```python
def format_view_count(views: int) -> str:
    """Format view count in compact notation."""
    if views < 1000:
        return str(views)
    elif views < 1_000_000:
        k = views / 1000
        return f"{k:.1f}K" if k < 10 else f"{int(k)}K"
    elif views < 1_000_000_000:
        m = views / 1_000_000
        return f"{m:.1f}M" if m < 10 else f"{int(m)}M"
    else:
        b = views / 1_000_000_000
        return f"{b:.1f}B" if b < 10 else f"{int(b)}B"
```

### Test Cases

```
Input: 890 → Output: "890"
Input: 5200 → Output: "5.2K"
Input: 45000 → Output: "45K"
Input: 350000 → Output: "350K"
Input: 1200000 → Output: "1.2M"
Input: 25000000 → Output: "25M"
Input: 450000000 → Output: "450M"
Input: 1100000000 → Output: "1.1B"
```

## Date Formatting

Always use ISO 8601 format: **YYYY-MM-DD**

### Rules

- Never use relative dates: "2 days ago", "this week", "recently"
- Never use long format: "January 15, 2025", "Jan 15, 2025"
- Always use: "2025-01-15"
- Leading zeros required: "2025-01-05" not "2025-1-5"

### Examples

```
✓ 2025-02-07
✓ 2024-12-25
✗ Feb 7, 2025
✗ 2/7/2025
✗ 2 days ago
```

## Title Truncation

### Rules

1. Maximum 80 characters including the ellipsis
2. If longer, append "…" (single Unicode ellipsis character: U+2026)
3. Prefer to truncate at word boundary when possible
4. Never leave partial words

### Examples

```
Original (95 chars):
"This is a really long YouTube video title that goes on and on and exceeds eighty characters limit"

Truncated (80 chars):
"This is a really long YouTube video title that goes on and on and exceeds…"

Original (88 chars):
"Complete Guide to Machine Learning: From Basics to Advanced Techniques in Production Systems"

Truncated (80 chars):
"Complete Guide to Machine Learning: From Basics to Advanced Techniques in…"
```

### Implementation Notes

- Count characters in the final output, including the "…"
- Use word boundary detection when possible to avoid breaking mid-word
- If no suitable word boundary exists within 70 chars, truncate at 79 chars and add "…"

## Token Optimization Impact

These formatting rules significantly reduce token usage:

- **Raw format**: "1,200,000 views" (4 tokens)
- **Compact format**: "1.2M" (1 token)
- **Savings per row**: ~3 tokens × 20 results = 60 tokens saved per search

For a 20-result table:
- Without optimization: ~400 tokens for view counts
- With optimization: ~40 tokens for view counts
- **Total reduction: 90% fewer tokens**
