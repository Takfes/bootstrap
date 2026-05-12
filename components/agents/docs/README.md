# CP-SAT Scheduling Bundle

Two skills + one subagent for building, debugging, and optimizing Google OR-Tools CP-SAT scheduling models with discipline.

## What's in here

```
.claude/
├── skills/
│   ├── cp-sat-modeling/
│   │   ├── SKILL.md                          # Build-phase methodology
│   │   └── references/
│   │       ├── primitives.md                 # Choosing CP-SAT primitives
│   │       ├── objectives.md                 # Objective design and soft constraints
│   │       ├── time-capacity.md              # Time, capacity, resources
│   │       ├── decomposition.md              # When and how to decompose
│   │       └── code-patterns.md              # CP-SAT-specific code patterns
│   └── cp-sat-debugging-and-performance/
│       ├── SKILL.md                          # Optimize-phase methodology
│       └── references/
│           ├── debugging.md                  # Infeasibility, log reading, wrong solutions
│           └── performance.md                # Triage, symmetry, redundant constraints, tuning
└── agents/
    └── cp-sat-scheduler.md                   # The worker subagent

examples/
└── cp-notes-user.md.example                  # Template for user-maintained context
```

## The architecture

**Two skills, two phases.** The build phase and the optimize phase are sequentially distinct activities. The agent loads the right skill based on what the user is doing.

- `cp-sat-modeling` — loaded for building, modifying, or designing scheduling models. Encodes the primitive selection ladder, objective design rules, time and capacity patterns, and decomposition strategy.
- `cp-sat-debugging-and-performance` — loaded for diagnosing infeasibility, fixing wrong-but-valid solutions, reading solver logs, and improving performance. Encodes diagnostic procedures and the performance triage hierarchy.

**Discipline is woven into both skills.** Rather than a separate "discipline" skill, the anti-patterns, novice-to-expert distinctions, failure modes, and moment-of-weakness disciplines are embedded in the skill that owns the relevant phase. The build-phase discipline (don't use big-M, characterize before coding, hard vs soft judgment) lives in the modeling skill. The optimize-phase discipline (don't reach for the constraint reflex, don't tune parameters before fixing the model) lives in the debugging-and-performance skill.

**The subagent decides when to load what.** No predefined loop. The agent reads the user's request, identifies the phase, loads the appropriate skill, and works.

**Two notes files, two ownerships.**
- `cp-notes-user.md` — user-maintained. The agent reads it at startup but never modifies it. Use for problem-domain context, project conventions, decisions you want preserved across sessions.
- `cp-notes-agent.md` — agent-maintained. The working artifact for the current session: modeling decisions log, performance work log, open questions, known limitations.

## Install

From your project root:

```bash
cp -r cp-sat-bundle/.claude/skills/cp-sat-modeling                    .claude/skills/
cp -r cp-sat-bundle/.claude/skills/cp-sat-debugging-and-performance   .claude/skills/
cp cp-sat-bundle/.claude/agents/cp-sat-scheduler.md                   .claude/agents/
```

Optionally, copy the user-notes template:

```bash
cp cp-sat-bundle/examples/cp-notes-user.md.example  cp-notes-user.md
# Then edit to capture your project's domain context, conventions, etc.
```

Confirm the agent is registered:

```bash
# In Claude Code:
/agents     # should list cp-sat-scheduler
/skills     # should list cp-sat-modeling and cp-sat-debugging-and-performance
```

## How invocation works

With the files in place, automatic delegation handles routing:

- "Build me a scheduling model for X" → `cp-sat-scheduler` is invoked, loads `cp-sat-modeling`, runs the build phase.
- "My CP-SAT model returns infeasible" → `cp-sat-scheduler` is invoked, loads `cp-sat-debugging-and-performance`, runs diagnostic procedures.
- "I built this model but it's slow" → `cp-sat-scheduler` is invoked, may load both skills (modeling for context, debugging-and-performance for the optimization work).

Explicit invocation also works:

```
> Use the cp-sat-scheduler subagent on this scheduling problem.
```

## Required environment

The bundle assumes:

- Python 3.x with `ortools` installed (`pip install ortools`).
- Claude Code or compatible environment with file-based skills and subagents.
- (Optional) Context7 MCP connector for OR-Tools API lookups on non-trivial code.

The agent will install missing dependencies on demand. Context7 is optional but recommended — without it, the agent falls back on training-data API memory, which may be stale for OR-Tools releases.

## Working with the notes files

`cp-notes-user.md` — maintain this yourself. The template in `examples/` shows the typical sections, but the file is just markdown — adapt to whatever helps you. The agent reads it at startup.

`cp-notes-agent.md` — the agent creates and maintains this. Don't delete entries while the agent is using the file; if you want a fresh session, delete the whole file before invoking the agent and it will create a new one.

## What this bundle does differently

The point of this bundle is not faster typing or auto-generated boilerplate. The point is **discipline**:

- Forcing the agent to characterize before coding.
- Forcing it to consider alternatives before locking in a primitive choice.
- Forcing it to diagnose before applying a fix.
- Forcing it to measure performance changes rather than tune by intuition.
- Forcing it to maintain a working record so decisions are durable.

Without that discipline, a CP-SAT assistant produces plausible-looking models that are brittle, slow, and hard to debug. The skill content encodes the discipline; the agent enforces it; the notes files make it durable.

## Tuning

If a skill feels too dense and is loaded on every task: move content from the SKILL.md body into the references. References are loaded on demand, body is loaded every time.

If the agent isn't reaching the right skill at the right time: sharpen the skill's frontmatter `description`. Vague descriptions under-trigger; over-specific ones over-narrow.

If the working notes feel like ceremony: they're not optional. The discipline of writing decisions before code, and measurements before the next move, is the point. If they feel like ceremony, the discipline isn't being applied.

## Honest caveats

- The `code-patterns.md` reference is a starter set. As more patterns emerge from real usage, extend it.
- The bundle is light on rostering-specific guidance (workforce scheduling specifics like fairness, complex shift patterns). The general methodology applies but you may need to supplement with domain content.
- The bundle assumes you've decided to use CP-SAT. It doesn't help you decide between CP-SAT, MIP, or heuristics for a given problem — that decision is upstream.
