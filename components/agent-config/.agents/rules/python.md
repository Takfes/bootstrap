---
paths:
  - "**/*.py"
---

# Python Conventions

Loads alongside `coding-conventions.md` for any `.py` file. Python 3.x, managed with **uv**.

## Style

- Type hints on all function signatures and class attributes. Use modern syntax: `X | None` instead of `Optional[X]`, `list[str]` instead of `List[str]`.
- f-strings over `.format()` or `%`.
- `pathlib.Path` over `os.path`.
- ruff for linting and formatting.
- Naming: `snake_case` functions/variables, `PascalCase` classes, `UPPER_SNAKE_CASE` constants, single leading underscore for private members.
- Imports: stdlib → third-party → local, blank line between groups.

## Data & Errors

- `dataclass` or `pydantic.BaseModel` for data containers; `@dataclass(frozen=True)` for immutable data.
- Catch specific exceptions only, never a bare `except:`. Use `raise ... from e` to preserve the exception chain.

## Docstrings

Google-style:

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

## Errors, concretely

```python
# Bad
raise ValueError("Invalid input")

# Good
raise ValueError(
    f"Query string cannot be empty. "
    f"Pass a non-empty string to fetch_results(). Got: {query!r}"
)
```

## Testing

pytest conventions:

```python
def test_fetch_results_raises_on_empty_query():
    with pytest.raises(ValueError, match="cannot be empty"):
        fetch_results("")

def test_fetch_results_respects_limit():
    results = fetch_results("python", limit=3)
    assert len(results) <= 3
```

## Project Structure

`pyproject.toml`, not `setup.py`. Dependency management via **uv**.
