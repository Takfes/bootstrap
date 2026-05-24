# Memory & Long-Term Learning

## Search Before Starting
Before any non-trivial task, search memory for relevant prior work. This prevents re-solving solved problems and surfaces preferences already established.

**Search using:**
- `mcp__plugin_claude-mem_mcp-search__smart_search` — general keyword search across sessions
- `mcp__plugin_claude-mem_mcp-search__timeline` — full chronological history of a project
- `mcp__plugin_claude-mem_mcp-search__get_observations` — fetch specific stored observations by ID

**Search before:**
- Starting a new feature or component (has this pattern been built before?)
- Debugging a recurring error (was this solved previously?)
- Choosing between approaches (has the user expressed a preference?)
- Drafting anything in the user's voice (what tone/format do they prefer?)
- Making a significant architectural decision (what decisions have already been made?)

## What to Persist
At the end of every task, ask: *"What from this session would be useful in a future conversation?"* Persist anything that qualifies.

**Persist:**
- **Lessons learned** — what worked, what failed, and the specific reason why
- **User preferences** revealed during the session (tools, formats, workflows they like or dislike)
- **Reusable patterns** — command templates, code idioms, workflow sequences that solved a recurring problem
- **Project decisions** — why a specific architecture, tool, or approach was chosen (the reasoning, not just the choice)
- **Domain knowledge** — concepts, terminology, or relationships specific to this workspace not evident from the code

**Do NOT persist:**
- Ephemeral task state with no future relevance
- Information derivable from reading the current codebase or git history
- General facts any competent agent would already know

## How to Save
Use the claude-mem plugin ([github.com/thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)) to persist. Structure entries for searchability:

- **Title:** Short and keyword-rich (e.g. "Preferred output format for search results")
- **Body:** Factual, concise, includes the *why* not just the *what*
- **Context:** Note the project, date, and task that generated the insight

## Cumulative Knowledge Base
The goal is a compound effect: each session should make future sessions faster and more accurate. Over time, memory accumulates:
- How this user thinks and works (patterns, preferences, shortcuts they use)
- What approaches have been tried and what their outcomes were
- The "why" behind decisions not captured in code or git history
- Recurring problems and their proven solutions

This eliminates re-explanation and allows operating at progressively higher levels of abstraction with each session.
