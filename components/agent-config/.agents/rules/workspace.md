# Workspace Layout

The `agents.io/` pattern — the IO contract for this project:

| Path         | Purpose                                                                                          |
| ------------ | -------------------------------------------------------------------------------------------------|
| `reference/` | Static lookup material — preferences, tooling guides, tracked lists. Rarely changes, not dated.  |
| `outputs/`   | Every dated task artifact — flat, one folder, filename does the categorizing.                    |
| `memory.md`  | Preferences and things worth remembering. Single flat list, edited in place.                     |
| `projects/`  | Code, scripts, deliverables — one subfolder per initiative, each with a README.                  |
| `prompts/`   | Reusable prompt templates, consulted proactively before matching tasks.                          |

## Stack

Python, managed with **uv**.

## Commands

Check for a `Makefile` or `justfile` in the relevant project folder — if present, those define the canonical commands. Don't invent commands if neither exists; ask.

## Documentation

Limited formal documentation today. Check each project's own README.md first. If you produce something that should be documented and isn't, say so.
