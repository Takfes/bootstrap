---
name: git-commit
description: Generate conventional commit messages for staged changes. Analyzes diffs, determines commit type, and creates well-formatted messages following Conventional Commits specification.
---

# Smart Commit Message Generator

Generate conventional commit messages for staged changes with proper formatting and description.

## When to Use This Skill

- **Single focused change**: Use when you have staged changes ready to commit
- **Need proper formatting**: When you want consistent, reviewable commit messages
- **Follow conventions**: Working with projects using Conventional Commits
- **Quick commits**: Fast way to generate professional commit messages
- **Multiple concerns**: For complex commits with multiple aspects, use Commit Wizard instead

## Core Process

### Step 1: Pre-check

Before generating a message, check for staged changes:

```bash
git diff --staged --quiet || true
```

If no staged changes exist, respond: "No staged changes to commit. Use `git add` to stage files first."

### Step 2: Analyze Staged Changes

Execute `git diff --staged` and extract:
- **Affected file paths** (from diff headers)
- **Line change counts** (insertions/deletions)
- **Change nature** (logic vs. formatting vs. docs)

Example analysis:
```
Files changed:
  - src/auth/login.py (15 lines added, 8 deleted)
  - tests/test_login.py (12 lines added)
  - docs/CHANGELOG.md (3 lines added)

Nature: Fix to session handling, added test coverage, docs update
```

### Step 3: Determine Commit Type

Refer to the [Conventional Commits Reference](references/conventional-commits.md) for the full type table.

### Step 4: Determine Scope

**Scope** provides context for where the change applies.

**When to include scope**:
- Changes are focused on a specific component/module
- File paths clearly indicate a subsystem

**How to extract scope**:
- Analyze the changed file paths
- Examples of scope extraction:
  - `src/api/routes.py` → `(api)`
  - `src/auth/login.py` → `(auth)`
  - `docs/GETTING_STARTED.md` → `(docs)`
  - `cli/commands/deploy.py` → `(cli)`

**When to omit scope**:
- Change spans multiple unrelated areas
- Changes affect the entire codebase
- Generic utility changes

### Step 5: Generate Subject Line

The subject is the most important part—it appears in logs and search results.

**Format**: `<type>(<scope>): <subject>`

**Rules**:
- **Maximum 50 characters** (strict limit for readability in logs)
- **Imperative mood**: "add" not "added", "fix" not "fixed"
- **Lowercase**: Start lowercase after the prefix
- **No trailing period**: Not needed
- **Specific and actionable**: Describe what the change does

**Examples**:
```
✓ feat(auth): add OAuth2 support for Google login
✓ fix(api): resolve race condition in payment processing
✓ docs(readme): update installation instructions
✓ refactor(core): simplify request routing logic
✗ Added OAuth support (past tense, too generic)
✗ fix(auth): Fixed a problem with authentication (too verbose)
```

### Step 6: Generate Body

The body explains the **what** and **why**, not the **how**.

**Format guidelines**:
- Wrap at **72 characters** per line
- Start with blank line after subject
- Use **bullet points** for multi-faceted changes
- Include **"Results:"** section for performance/optimization/refactor

**For focused changes (1-2 files)**:
Use 1-2 sentence explanation of rationale:

```
fix(checkout): resolve payment processing timeout

The payment gateway was timing out due to sequential processing
of items instead of batch operations. This change implements
concurrent batch processing, reducing average processing time
from 45s to 12s.
```

**For substantial changes (3+ files, 50+ lines, multiple directories)**:
Use bullet points with results:

```
feat(auth): implement multi-factor authentication

- Add MFA enrollment flow in user settings
- Create SMS delivery service integration
- Add MFA verification during login
- Update session management to check MFA status
- Add database migrations for MFA configuration

Results:
- 3 new API endpoints
- 2 new database tables
- SMS verification compatible with Twilio and AWS SNS
```

**For breaking changes**:
Provide detailed explanation and migration path:

```
feat(api)!: change user endpoint response format

BREAKING CHANGE: The user endpoint now returns `userId` instead
of `id`. All API consumers must be updated to use the new field
name.

Migration guide:
1. Replace all references to `user.id` with `user.userId`
2. Update GraphQL queries if using our GraphQL API
3. Test thoroughly in staging before deploying to production

Fixes #456
```

### Step 7: Add Footer

Include relevant footer information:

**Typical footers**:
- `BREAKING CHANGE: description` (mandatory if breaking change)
- `Closes #123` (closes an issue)
- `Fixes #456` (alternative to Closes)
- `Refs #789` (references without closing)
- `Co-Authored-By: Name <email>` (credit co-authors)

**Always include**:
```
Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

### Step 8: Execute Commit

Use the heredoc format to safely pass the entire message:

```bash
git commit -m "$(cat <<'EOF'
<subject>

<body>

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

## Real-World Examples

### Example 1: Simple Bug Fix

**Staged changes**: Single file with 3 lines changed
**Diff summary**: Fixed off-by-one error in pagination

```
git commit -m "$(cat <<'EOF'
fix(pagination): correct offset calculation in list endpoint

The pagination offset was calculated as (page - 1) * size + 1,
which caused the first item to be skipped. Changed to standard
formula: (page - 1) * size.

Fixes #234
Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

### Example 2: Feature Addition

**Staged changes**: Multiple files (feature + tests)
**Diff summary**: Added dark mode toggle

```
git commit -m "$(cat <<'EOF'
feat(ui): add dark mode support with system preference detection

- Add theme toggle in settings menu
- Detect system dark mode preference on first visit
- Persist theme preference in localStorage
- Update all color tokens for dark mode
- Add dark mode styles for core components

Results:
- Smooth transitions between themes
- Automatic theme sync with system settings
- No layout shift during theme switch
Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

### Example 3: Documentation

**Staged changes**: README and docs folder
**Diff summary**: Added API documentation

```
git commit -m "$(cat <<'EOF'
docs(api): add comprehensive API reference guide

Added detailed documentation for all public API endpoints with
examples for each HTTP method. Includes authentication guide and
rate limiting information.

Closes #567
Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

### Example 4: Refactoring

**Staged changes**: Module reorganization
**Diff summary**: Extract utilities to reduce duplication

```
git commit -m "$(cat <<'EOF'
refactor(core): extract common validation logic to utilities

- Move email/phone validation to shared validators module
- Consolidate error formatting into single utility
- Remove duplicate validation logic from 4 modules
- Update imports across 8 files

Results:
- 340 lines of duplicated code eliminated
- Single source of truth for validation rules
- Easier to update validation logic in future
Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

## Best Practices

### Do's

- ✓ **Keep subjects concise**: 50 characters forces clarity
- ✓ **Use imperative mood**: Matches git's convention ("fix bug" vs "fixed bug")
- ✓ **Reference issues**: Link commits to tracking tickets
- ✓ **Include WHY**: The body should explain rationale
- ✓ **One logical change per commit**: Easier to review and revert
- ✓ **Be specific**: "fix validation" is better than "fix bug"

### Don'ts

- ✗ **Don't exceed 50 chars in subject**: Forces discipline and readability
- ✗ **Don't use past tense**: Use "add" not "added"
- ✗ **Don't mix concerns**: Separate refactoring from features
- ✗ **Don't skip the body**: Explain context and rationale
- ✗ **Don't use generic messages**: "fix stuff" or "updates" add no value

## Comparison with Commit Wizard

Use **Smart Commit** when:
- You have a single, focused change to commit
- All changes logically belong together
- You just need to generate the message quickly

Use **Commit Wizard** (`/git-commit-wizard`) when:
- You have multiple uncommitted changes spanning different concerns
- You want to split work into atomic, reviewable commits
- You're preparing a clean commit history before pushing

## Integration with CI/CD

Conventional commits enable automation:

- **Changelog generation**: Tools automatically create changelogs from `feat` and `fix` commits
- **Semantic versioning**: `feat` → MINOR version, `fix` → PATCH version
- **Release notes**: Commits are automatically grouped by type
- **Statistics**: Track what type of work the team does

## Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Git Commit Best Practices](https://chris.beams.io/posts/git-commit/)
- [Semantic Versioning](https://semver.org/)
- [commitlint](https://commitlint.js.org/) - Enforce conventional commits

## Related Skills

- **`/git-commit-wizard`** — For multiple unrelated changes that need organizing into atomic commits
