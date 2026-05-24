---
name: search-perplexity
description: Search Perplexity.ai using Chrome browser automation and return results as structured markdown. Use this skill whenever the user asks to "search perplexity", "ask perplexity", "look this up on perplexity", "research on perplexity", or wants live web-sourced answers via Perplexity. Trigger even if the user just says "perplexity: <query>" or "use perplexity to find...". Always prefer this skill over web search when the user explicitly mentions Perplexity.
---

# Perplexity Search

Use this skill to run a search on Perplexity.ai via Chrome browser automation and return the full response as clean, structured markdown.

## When to use

Trigger when the user asks to search or research something using Perplexity, e.g.:
- "search perplexity for X"
- "ask perplexity about X"
- "look this up on perplexity: X"
- "use perplexity to research X"
- "perplexity: X"

## Parameters

| Parameter | Default | Override Examples |
|-----------|---------|-------------------|
| query | (required) | Any natural language search term |
| limit | Full answer | "give me top 5 points", "summarize in 3 bullets" |

## Step-by-step workflow

### Step 1 — Connect to Chrome

Call `mcp__claude-in-chrome__tabs_context_mcp` with `createIfEmpty: true`.

- If it returns available tabs → proceed to Step 2.
- If it returns an error ("extension not connected") → tell the user: *"Chrome extension is disconnected. Please click the Claude extension icon in Chrome to reconnect, then let me know."* Wait for the user to confirm reconnection, then retry once.

### Step 2 — Open a fresh tab

Always create a new tab with `mcp__claude-in-chrome__tabs_create_mcp`. Never reuse an existing tab. Note the new `tabId`.

### Step 3 — Navigate to Perplexity

Navigate the new tab to `https://www.perplexity.ai` using `mcp__claude-in-chrome__navigate`.

Take a screenshot to confirm the page loaded. If it doesn't show the Perplexity search UI within 5 seconds, navigate again.

### Step 4 — Dismiss any popups

Take a screenshot. If a modal/popup is visible (e.g., cookie banner, Google Drive promo), click its close/dismiss button before proceeding. Don't let a popup block the search box.

### Step 5 — Enter the search query

Click the search input box (visible in the centre of the page) and type the user's query using `mcp__claude-in-chrome__computer` with `action: type`.

**Important:** Type a plain-text version of the query. Strip markdown formatting (bold, headers, bullet symbols) — Perplexity's input is a plain text field.

Then press Enter (`mcp__claude-in-chrome__computer` with `action: key`, `text: Return`).

### Step 6 — Wait for the answer to stream

Perplexity streams its answer. Wait for it to finish:

1. Wait 5 seconds (`action: wait`, `duration: 5`)
2. Take a screenshot — check if the answer is still loading (animated dots, partial text, spinner)
3. If still loading, wait another 5 seconds and check again
4. Repeat until the answer appears stable (no loading indicators) — maximum 3 wait cycles (15 seconds total)

### Step 7 — Collect the full response

Use `mcp__claude-in-chrome__get_page_text` to extract the full page text. This gives the complete answer including all sections.

If `get_page_text` fails, fall back to `mcp__claude-in-chrome__read_page` with `filter: all` and extract the answer content from the accessibility tree.

### Step 8 — Format and present results

Transform the raw text into clean markdown. Output the main answer content directly with `##` headers, bullet points, and tables as needed, followed by a `## Sources` section.

Guidelines for formatting:
- Start directly with the answer content — no title header or query blockquote
- Use `##` headers to break up major sections in the answer
- Use bullet points for lists of items or features
- Use a markdown table if the answer contains comparative data (e.g., multiple options with attributes)
- Keep the content faithful to Perplexity's response — don't summarise or paraphrase heavily
- Strip UI chrome (navigation labels, "Ask a follow-up", button labels) from the output
- End with a `## Sources` section listing any source domains mentioned in the response

### Step 9 — Offer to save

After presenting the formatted results, ask:

> "Would you like me to save this to disk?"

If yes, save to the **current working directory** using this filename format:

```
perplexity-{brief-query-slug}-{YYYYMMDDHHmm}.md
```

Where `{brief-query-slug}` is 3–5 lowercase hyphenated words from the query (e.g., `ml-dataset-ideas`, `best-python-frameworks`).

---

## Error handling

| Problem | Recovery |
|---|---|
| Extension disconnected | Ask user to reconnect, retry once |
| Page doesn't load | Re-navigate, retry once |
| Popup blocks search box | Close popup, then proceed |
| Answer still loading after 15s | Collect whatever is visible, note it may be partial |
| `get_page_text` fails | Fall back to `read_page` accessibility tree |

## Performance tips

- Always load the ToolSearch for chrome tools at the start if not already loaded: `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__get_page_text`
- Minimise screenshot calls — only take them when needed to verify state
- Use `get_page_text` (fastest) over `read_page` (verbose) for result collection
- Don't scroll or interact further after the answer is collected — get in, get the text, get out

See `references/browser-patterns.md` for detailed Chrome automation patterns and efficiency guidelines.

## Related Skills

**Other search skills:** `/search-web` · `/search-youtube` · `/search-zotero`
