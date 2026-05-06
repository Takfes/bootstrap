# Chrome Automation Patterns for Perplexity

## Tool Loading (Once Per Session)

Load all required Chrome tools at session start:

```
ToolSearch: select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__get_page_text
```

## Efficiency Guidelines

- Minimise screenshot calls — only take them when needed to verify state
- Use `get_page_text` (fastest) over `read_page` (verbose) for result collection
- Don't scroll or interact further after the answer is collected — get in, get the text, get out
- Maximum 3 wait cycles (15 seconds total) for streaming completion

## Tab Management

- Always create a new tab for each search (never reuse existing tabs)
- Use `createIfEmpty: true` on tabs_context_mcp
- Note the tabId from tabs_create_mcp for all subsequent calls

## Wait Strategy

1. Wait 5 seconds after submitting query
2. Take screenshot — check for loading indicators (dots, spinner, partial text)
3. If loading: wait another 5 seconds and recheck
4. Repeat up to 3 times total
5. If still loading after 15s: collect what's available, note it may be partial
