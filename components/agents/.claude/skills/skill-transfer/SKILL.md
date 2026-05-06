---
name: skill-transfer
description: Consolidate and sync skills across agent repositories (.claude/skills, .gemini/skills, .agents/skills, .github/skills). Use this skill when you need to find duplicate skills across repositories, identify conflicts, and unify them into a superset. Produces a concise, decision-focused report showing what can be automatically merged and what requires your input. Use this whenever you've updated skills in one repo and want to propagate them elsewhere, or when consolidating multiple skill sources into a unified set.
compatibility: Requires local filesystem access; works with any project using .claude/, .gemini/, .agents/, .github/ structure
---

# Skill Transfer

Discover, compare, and consolidate skills across your agent repositories. Produces a minimal report with clear decision points for conflicts.

## What It Does

1. **Scans** `.claude/skills/`, `.gemini/skills/`, `.agents/skills/`, `.github/skills/` (only those you specify)
2. **Compares** skills with the same name using file hashing
3. **Classifies** into:
   - **Auto-resolvable**: Identical skills or new skills to migrate
   - **Conflicts**: Same name, different content — your decision required
4. **Reports** in compact format with enumerated decision points
5. **Does NOT apply changes** — you review and approve first

## How to Use

### Invoke the skill

Tell me:
- **Repositories to scan** (which of `.claude`, `.gemini`, `.agents`?)
- **Direction of transfer** (typically: which is source, which is destination?)

Example:
```
Run skill-transfer:
- Scan: .claude/skills and .gemini/skills
- Transfer from: .claude → .gemini
- Only show skills for: claude and gemini (skip agents, github)
```

### You get a report

The report shows:
- **Summary** — stats at a glance
- **Auto-resolvable** — 14 skills ready to migrate (no action needed)
- **Conflicts** — 2 items requiring your choice (enumerated 1, 2, etc.)

### You decide on conflicts

For each conflict, you pick:
- **A)** Use source version
- **B)** Use destination version  
- **C)** Keep both separate

Reply with format: `1.A 2.B`

### I apply your decisions

Once you confirm, I:
- Copy/update skill files to destination repo(s)
- Preserve your preferences from previous runs
- Report what was transferred

## Report Format

```
# Skill Transfer Report
Scope: .claude/skills → .gemini/skills (also scanned: .github/skills) | Date: YYYY-MM-DD HH:MM UTC

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total skills discovered: 28
Auto-resolvable: 14 (12 synced, 2 new)
Conflicts requiring decision: 2

After transfer: .gemini/skills/ will have 42 skills (+14 new)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ AUTO-RESOLVABLE (14 SKILLS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Synced (identical in both):
  [skill-name-1], [skill-name-2], ...

New to destination (from source):
  [skill-name-1], [skill-name-2], ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ CONFLICTS — YOUR DECISION NEEDED (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─ 1. [skill-name]
├─ Source: v1.2 (320 lines, feature X)
├─ Dest: v1.0 (280 lines, stable)
└─ Choose: [ ] A) Source  [ ] B) Dest  [ ] C) Keep both

┌─ 2. [skill-name]
├─ Source: SKILL.md + scripts/ + references/
├─ Dest: SKILL.md + scripts/ + references/ + assets/
└─ Choose: [ ] A) Source  [ ] B) Dest  [ ] C) Keep both

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reply with decisions: 1.A 2.B
```

## Implementation Notes

- **Skill names match** when directory names are identical across repos
- **File comparison** uses SHA256 hashing of all files under skill directory
- **Identical = identical**: All files in both versions hash to the same value
- **Conflict = different hashing**: Content differs; user picks which to keep
- **No merging**: Only copy/overwrite; conflicts require explicit user choice
- **skill-transfer excluded**: This skill is not included in the superset to avoid bootstrap issues

## When to Use This Skill

- You've updated skills in `.claude/skills/` and want to sync to `.gemini/` or `.github/`
- You're consolidating your agent setup and need a unified skill set across repositories
- You have duplicate skills scattered across repos and want a single source of truth
- You're onboarding a new agent/CLI and need it to have access to all your existing skills
- You want to audit what skills exist where and see what's out of sync
- You want to include GitHub-hosted skills (`.github/skills/`) in a cross-repo sync
