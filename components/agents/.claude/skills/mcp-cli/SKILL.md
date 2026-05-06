---
name: mcp-cli
description: Talk to MCP (Model Context Protocol) servers from the shell with the `mcp-cli` binary. Use this skill whenever the user mentions MCP, asks to list/inspect/call MCP tools, or names one of the configured servers — context7, zotero, tavily-remote-mcp, playwright, sequentialthinking, vibe_kanban, notebooklm-mcp — even casually ("ask context7 about react hooks", "search my zotero for transformer papers", "use tavily to look up X"). Also trigger when the user wants to discover what MCP servers expose, debug an MCP server, prototype a tool call before wiring it into a permanent integration, or test an MCP server without polluting the agent context with a permanent install. Prefer this skill over generic web search or file tools when the user references MCP, an MCP server name, or a tool that lives behind one.
---

# mcp-cli

`mcp-cli` is a thin command-line interface to MCP servers. Use it to discover what a server exposes, inspect tool schemas, and invoke tools — without registering the server as a permanent integration.

Reference: https://github.com/philschmid/mcp-cli

## When to reach for it

- The user mentions MCP, a specific server name, or a capability that lives behind one (e.g. _“search my zotero”_, _“ask context7”_, _“run a tavily search”_)
- A one-off call is enough — no need to commit a server to permanent config
- You need to _see_ a tool's input schema before calling it
- You're debugging or prototyping an MCP server

## Configured servers

Defined in `.claude/skills/mcp-cli/servers.json`:

| Server               | Type         | What it's for                                     |
| -------------------- | ------------ | ------------------------------------------------- |
| `context7`           | npx          | Up-to-date library/API documentation lookup       |
| `notebooklm-mcp`     | local binary | NotebookLM automation (notebooks, sources, notes) |
| `playwright`         | npx          | Browser automation and scraping                   |
| `sequentialthinking` | npx          | Step-by-step structured reasoning                 |
| `tavily-remote-mcp`  | http         | Web search and research over HTTP                 |
| `vibe_kanban`        | npx          | Kanban / task board management                    |
| `zotero`             | local binary | Search and retrieve from local Zotero library     |

## Workflow: Discover → Inspect → Execute

This is the canonical loop. Skipping discovery leads to guessed parameter names and avoidable errors.

1. **Discover** — `mcp-cli` lists every server and its tool names.
2. **Explore** — `mcp-cli <server>` lists that server's tools with parameter signatures. Add `-d` for descriptions.
3. **Inspect** — `mcp-cli <server>/<tool>` (or `mcp-cli info <server> <tool>`) returns the full JSON input schema. Read this before crafting arguments.
4. **Execute** — `mcp-cli <server>/<tool> '<json>'` (or `mcp-cli call <server> <tool> '<json>'`) runs the tool.

## Commands

| Command                                 | Output                               |
| --------------------------------------- | ------------------------------------ |
| `mcp-cli`                               | List all servers and tool names      |
| `mcp-cli -d`                            | Same, with descriptions              |
| `mcp-cli <server>`                      | Show tools with parameter signatures |
| `mcp-cli <server> -d`                   | Same, verbose                        |
| `mcp-cli <server>/<tool>`               | Get tool's JSON input schema         |
| `mcp-cli <server>/<tool> '<json>'`      | Call the tool with arguments         |
| `mcp-cli call <server> <tool> '<json>'` | Same, explicit subcommand form       |
| `mcp-cli grep "<glob>"`                 | Search tools by name across servers  |

### Flags

| Flag                           | Purpose                            |
| ------------------------------ | ---------------------------------- |
| `-d, --with-descriptions`      | Include tool descriptions          |
| `-j, --json`                   | JSON output (for piping into `jq`) |
| `-r, --raw`                    | Raw text content (no formatting)   |
| `-c, --config <path>`          | Use a non-default config file      |
| `-h, --help` / `-v, --version` | Help / version                     |

### Parameter signatures

When `mcp-cli <server>` prints tool signatures, the shape is:

| Notation      | Meaning                   |
| ------------- | ------------------------- |
| `param:str`   | Required string           |
| `param:num`   | Required number           |
| `param:bool`  | Required boolean          |
| `param:str[]` | Required array of strings |
| `[param:str]` | Optional parameter        |

Match the JSON exactly to these — wrong types are the most common cause of `exit 2` errors.

## Examples (using configured servers)

### Discovery

```bash
# Everything available
mcp-cli

# Just zotero, with descriptions
mcp-cli zotero -d

# Find every tool whose name mentions "search"
mcp-cli grep "*search*"
```

### context7 — documentation lookup

```bash
# See the schema first
mcp-cli context7/resolve-library-id

# Resolve a library, then fetch its docs
mcp-cli context7/resolve-library-id '{"libraryName": "react"}'
mcp-cli context7/get-library-docs '{"context7CompatibleLibraryID": "/facebook/react", "topic": "hooks", "tokens": 5000}'
```

### zotero — local library search

```bash
mcp-cli zotero/zotero_semantic_search '{"query": "retrieval augmented generation", "limit": 10}'
mcp-cli zotero/zotero_get_item_fulltext '{"item_key": "ABCD1234"}'
```

### tavily-remote-mcp — web research over HTTP

```bash
mcp-cli tavily-remote-mcp/tavily_search '{"query": "claude agent skills 2026", "max_results": 5}'
```

### playwright — browser automation

```bash
mcp-cli playwright/browser_navigate '{"url": "https://example.com"}'
mcp-cli playwright/browser_snapshot '{}'
```

### sequentialthinking — structured reasoning

```bash
mcp-cli sequentialthinking/sequentialthinking '{
  "thought": "Break this problem into sub-questions",
  "thoughtNumber": 1,
  "totalThoughts": 5,
  "nextThoughtNeeded": true
}'
```

### vibe_kanban — task board

```bash
mcp-cli vibe_kanban/list_projects '{}'
```

### notebooklm-mcp — NotebookLM automation

```bash
mcp-cli notebooklm-mcp/list_notebooks '{}'
```

### Piping and stdin

```bash
# JSON output → jq
mcp-cli zotero/zotero_search_items '{"query": "transformers"}' --json | jq '.content[0].text'

# Heredoc for JSON containing single quotes
mcp-cli context7/get-library-docs <<'EOF'
{"context7CompatibleLibraryID": "/vercel/next.js", "topic": "app router"}
EOF

# Read args from a file
cat args.json | mcp-cli playwright/browser_navigate
```

## Configuration

`mcp-cli` resolves its server config in this order (first match wins):

1. `MCP_CONFIG_PATH` environment variable
2. `-c/--config <path>` argument
3. `./mcp_servers.json` (cwd)
4. `~/.mcp_servers.json`
5. `~/.config/mcp/mcp_servers.json`

The skill's local config lives at `.claude/skills/mcp-cli/servers.json`. To use it explicitly:

```bash
mcp-cli -c .claude/skills/mcp-cli/servers.json
```

### Config shape

stdio server (most common):

```json
{ "command": "npx", "args": ["-y", "@upstash/context7-mcp@latest"] }
```

HTTP server:

```json
{ "type": "http", "url": "https://mcp.tavily.com/mcp/" }
```

With env vars (zotero pattern):

```json
{
  "command": "/Users/takis/miniforge3/bin/zotero-mcp",
  "args": [],
  "env": { "ZOTERO_LOCAL": "true", "ZOTERO_EMBEDDING_MODEL": "default" }
}
```

`${VAR_NAME}` interpolation inside `args`/`env` is supported — useful for tokens (`"GITHUB_TOKEN": "${GITHUB_TOKEN}"`).

## Useful environment variables

| Var               | Purpose                                               |
| ----------------- | ----------------------------------------------------- |
| `MCP_CONFIG_PATH` | Override config path                                  |
| `MCP_TIMEOUT`     | Request timeout in seconds (default 1800)             |
| `MCP_DEBUG`       | Verbose debug output to stderr                        |
| `MCP_NO_DAEMON`   | Disable connection caching (force fresh server start) |
| `MCP_MAX_RETRIES` | Retry count on transient failures (default 3)         |

## Exit codes

| Code | Meaning                                                         | Typical fix                                 |
| ---- | --------------------------------------------------------------- | ------------------------------------------- |
| `0`  | Success                                                         | —                                           |
| `1`  | Client error: bad CLI args, missing config, unknown server/tool | Re-check the discover/inspect steps         |
| `2`  | Server error: tool ran but returned an error                    | Check parameter types and the tool's schema |
| `3`  | Network error                                                   | Server URL, auth, or connectivity           |

## Troubleshooting

- **`unknown server` / `unknown tool`** — run `mcp-cli` to confirm the exact name; servers may not be picked up if the wrong config is loaded (use `-c`).
- **JSON parse errors** — wrap the JSON in single quotes and use double quotes inside, or use a heredoc / file. Shell expansion of `$` and backticks is a common culprit.
- **Server seems to hang** — first call to a server may spawn an `npx`/binary install; give it 10–30s. Set `MCP_DEBUG=1` to see what's happening.
- **Tool returns exit 2** — almost always a schema mismatch. Re-run `mcp-cli <server>/<tool>` and align JSON keys/types exactly.
- **Permission denied** — for filesystem-style servers, ensure the configured allowed paths cover what you're asking for.

## Best practices

- **Discover before you call.** A two-second `mcp-cli <server>/<tool>` saves a guess-and-retry loop.
- **Use `--json` when chaining.** Anything you'll pipe to another tool should be machine-readable.
- **Single-quote JSON arguments.** Stops the shell from mangling `$`, backticks, and `!`.
- **One server, many calls?** Stay in the same shell — `mcp-cli` caches the connection (unless `MCP_NO_DAEMON` is set), so subsequent calls are fast.
- **Don't promote to permanent config too early.** `mcp-cli` is the right place to evaluate a server before deciding it's worth a permanent integration.
