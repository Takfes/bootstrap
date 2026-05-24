# Coding Conventions

## Python
- Primary language: Python 3.x
- Use type hints for all function signatures and class attributes
- Prefer f-strings over `.format()` or `%`
- Naming: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants
- Organize imports: stdlib → third-party → local (blank line between each group)

## Code Style

**Docstrings:** All public functions, classes, and modules — Google-style format:
```python
def fetch_results(query: str, limit: int = 10) -> list[dict]:
    """Fetch search results for a query.

    Args:
        query: The search string to look up.
        limit: Maximum number of results to return.

    Returns:
        A list of result dicts, each with keys 'title', 'url', 'snippet'.

    Raises:
        ValueError: If query is empty.
        HTTPError: If the upstream API returns a non-2xx status.
    """
```

- Add inline comments for non-obvious logic — not for what the code does, but why
- Keep functions focused and single-purpose; if a function needs a "and" in its description, split it

## Behaviour

**Ask before major changes.** Major changes are:
- Refactoring a function or class interface (rename, reorder, remove parameters)
- Restructuring a module or moving files
- Changing behaviour that existing callers depend on
- Any edit affecting more than ~30 lines outside the immediate task scope

Minor edits (fixing a bug, adding a parameter with a default, adding a new function) do not require confirmation.

**Explain decisions** — one sentence is enough: "Using a dict here instead of a list for O(1) lookup."

**Error handling:** Messages must answer three questions — what failed, why, and what to try next:
```python
# Bad
raise ValueError("Invalid input")

# Good
raise ValueError(
    f"Query string cannot be empty. "
    f"Pass a non-empty string to fetch_results(). Got: {query!r}"
)
```

Prefer explicit over implicit. Never swallow exceptions silently.

## Testing
Write tests for:
- All new public functions
- Any logic with branching (if/else, loops with conditions, exception paths)
- Bug fixes — add a regression test that would have caught the bug

**Non-trivial = has branching, state, or side effects.** Pure single-path transformations (e.g. `return x * 2`) don't need tests.

Use pytest conventions:
```python
def test_fetch_results_raises_on_empty_query():
    with pytest.raises(ValueError, match="cannot be empty"):
        fetch_results("")

def test_fetch_results_respects_limit():
    results = fetch_results("python", limit=3)
    assert len(results) <= 3
```

## Tool Preferences
Always use dedicated tools over Bash equivalents:
| Task | Use | Not |
|------|-----|-----|
| Read a file | `Read` | `cat`, `head`, `tail` |
| Search content | `Grep` | `grep`, `rg` |
| Find files | `Glob` | `find`, `ls` |
| Edit a file | `Edit` | `sed`, `awk` |
| Create a file | `Write` | `echo >`, heredoc |

Reserve `Bash` for system commands that have no dedicated tool equivalent.

## Guardrails
- Stay within the scope of what was requested — no unsolicited refactoring or cleanup
- Don't remove existing functionality without explicit confirmation
- Choose the simplest working solution over a clever one
- Never skip safety checks (`--no-verify`, `--force` push) without explicit user instruction
- Don't add error handling, fallbacks, or validation for scenarios that cannot happen
