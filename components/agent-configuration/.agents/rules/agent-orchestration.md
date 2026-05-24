# Agent Orchestration

## Parallelisation

Always identify tasks that can run in parallel before starting any multi-step work. Build an explicit dependency graph first.

**When to parallelise:**

- Multiple reads, searches, or file accesses with no shared state
- Independent subagent research tasks (e.g. read file A, read file B, read file C simultaneously)
- Generating multiple options or variants at the same time
- Running verification while writing documentation

**When NOT to parallelise:**

- Task B requires the output of Task A as its input
- Both tasks write to the same file
- Sequential reasoning chains where earlier output informs later steps

**Dependency graph pattern:**

```
Task A ──┐
Task B ──┼──► Task D ──► Task E
Task C ──┘
```

Tasks A, B, C run in parallel → Task D consumes their combined output → Task E follows D.

**Execution rule:** Never serialise what can be parallelised. Issue all independent tool calls in a single message.

## Tool Chaining

Combine tools into pipelines that accomplish complex objectives in fewer round-trips.

**The canonical chain: Search → Plan → Execute**

1. **Gather** — Grep, Glob, Read, WebSearch to collect raw information
2. **Synthesise** — Plan agent or sequential thinking to turn information into a strategy
3. **Execute** — Edit, Write, Bash to carry out the plan

**Other common chains:**

- **Explore → Implement → Verify**: Explore subagent → Edit/Write → run tests or confirm output
- **Read → Summarise → Decide**: Read multiple files → synthesise findings → AskUserQuestion with informed options
- **Search → Optimise → Dispatch**: Find relevant context → craft optimised prompt → dispatch subagent with that prompt

**Composition rule:** Prefer reusable, discrete capabilities over single-purpose pipelines. Each tool in the chain should do one thing; the chain produces the complex result.

## Agent & Model Deployment

Deploy specialised subagents for distinct tasks rather than doing everything in the main context.

**When to deploy a subagent:**

- The task requires deep exploration of a large codebase (would flood main context with noise)
- The task is independent and its output feeds a later step
- Multiple independent tasks can run simultaneously (dispatch them all at once)
- The task requires a specialised agent type (Explore, Plan, code-reviewer)

**Model selection heuristic:**
| Task type | Model |
|-----------|-------|
| Complex reasoning, architecture, planning | Strongest (Opus) |
| Code generation, writing, analysis | Mid-tier (Sonnet) |
| Simple retrieval, file listing, grep-style search | Lightest (Haiku) |
| Default when uncertain | Match current session model |

**Subagent type selection:**

- `Explore` — file search, codebase understanding, quick reads (read-only)
- `Plan` — architecture decisions, implementation strategy design
- `general-purpose` — multi-step autonomous tasks requiring writes
- `superpowers:code-reviewer` — after completing a significant implementation step

### When NOT to Deploy

Multi-agent deployment is **not** warranted when:

- The task can be completed in fewer than 3 tool calls
- No meaningful parallel work is available
- Coordination overhead would exceed the benefit
- The task is purely sequential reasoning with no specialist depth requirements

If none of the "when to deploy" conditions above are met → state "one-man job" and proceed directly without offering staffing.

### Subagents vs Agent Teams

Two architecturally distinct deployment modes:

| | Subagents | Agent Teams |
|---|---|---|
| **Architecture** | Hub-and-spoke; orchestrator dispatches and collects | Mesh; agents share a task list and message each other directly |
| **Context** | Own context window; results return to caller | Own context window; fully independent |
| **Coordination** | Orchestrator owns all coordination and synthesis | Agents self-coordinate peer-to-peer via shared task list |
| **Best for** | Parallel focused tasks where only the result matters | Complex work requiring agents to discuss, iterate, and build on each other |
| **Token cost** | Lower — results summarised back to main context | Higher — each teammate is a full Claude instance |
| **Default choice** | Yes — unless peer collaboration is genuinely needed | Reserve for truly collaborative multi-agent workflows |

Agent teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (already enabled in project settings).

### Agent Inventory

Before deploying any agent, scan `.claude/agents/` to identify available candidates:

- **Named/custom agents** (e.g. *Alfie — Data Scientist*) take priority — these are the preferred cast
- **Generic agents** serve as fallbacks for roles not yet covered by a named agent

### Named Agents Convention

Custom agents built for recurring roles get human names and a role title (e.g. *Alfie — Data Scientist*, *Ali — Reporting*, *Margot — Scrum Master*). These accumulate over time as a recognisable cast.

- The `name` field in frontmatter is a technical slug: `alfie-data-scientist`
- The human name and role appear in the system prompt: "You are Alfie, a data scientist specialising in…"
- Named agents enable fast, conversational staffing: "get Ali and Alfie on this"

### Context Passing

Every agent dispatch must include:

- The task description
- Relevant excerpts from the plan/spec
- Required output format
- What the downstream consumer of this output needs

Agents dispatched without context work blind and produce outputs that require costly correction passes.

### Output Synthesis

The orchestrator owns synthesis. When multiple subagents return results, the orchestrator — not a subagent — assembles the final output. A specialist synthesis agent (e.g. `research-analyst`) is only deployed if the synthesis itself is complex enough to warrant it.

### Failure & Fallback

If a subagent returns incomplete or unusable output:

1. One retry with a refined prompt — ensure it includes all four fields from the Context Passing section above (task description, plan excerpts, output format, downstream consumer needs)
2. If still failing → escalate to the orchestrator to handle inline

Do not loop indefinitely. Retrying the same failing prompt wastes tokens and time.

## Project Staffing

Decision logic for when and how to initiate project staffing. Process steps live in `prompts/staff-project.md`.

### One-Man Job Assessment

After any plan is written, assess whether multi-agent deployment is warranted. It is warranted if **at least one** of these is true:

- The plan has 2+ clearly independent workstreams that could run in parallel
- The plan requires capabilities spanning distinct domains (e.g. data engineering + ML + reporting)
- The volume of work in a single phase exceeds what one context window can handle well
- The plan has distinct phases where specialist depth matters at each stage

If none apply → state "one-man job" and proceed. Do not offer staffing.

### Staffing Trigger

When multi-agent deployment is warranted: offer staffing explicitly before implementation begins.

- If user accepts → follow `prompts/staff-project.md` to construct the roster
- If user declines → proceed as orchestrator, deploying agents ad-hoc using the parallelisation and deployment rules above

Staffing can be re-triggered at any phase boundary — e.g. when moving from research to implementation, or when a new capability gap appears mid-project.
A phase boundary is any point where the nature of work changes — e.g. research to implementation, implementation to testing, or when a new deliverable type is introduced.

### Mode Selection

Use the Subagents vs Agent Teams table above. Default to **subagents** unless agents genuinely need to message each other directly and build on each other's outputs in real time — agent teams are the exception, not the default. The staffing prompt determines mode per phase.
