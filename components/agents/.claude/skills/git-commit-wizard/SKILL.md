---
name: git-commit-wizard
description: Guide user through organizing and committing multiple changes in one session. Groups related files, proposes atomic commits, and generates proper messages following Conventional Commits specification.
---

# Commit Wizard

Systematically organize and commit multiple changes in one session with proper grouping and messaging.

## When to Use This Skill

- **Multiple uncommitted changes**: Spanning different concerns and file locations
- **Want clean history**: Organizing work into atomic, reviewable commits
- **Before pushing**: Preparing a professional commit history
- **Complex sessions**: After significant refactoring or multi-feature work

**Skip if**: You have a single focused change—use `/git-commit` directly instead.

## Core Process

### Step 1: Analyze All Changes

Get a comprehensive view of what's been modified:

```bash
git status --short        # Show file states
git diff --stat          # Show changed files and line counts
git diff --name-status   # Show what happened to each file (M/A/D)
```

Example output to analyze:
```
 M src/auth/login.py
 M tests/test_login.py
 M docs/CHANGELOG.md
?? src/auth/oauth.py
 M src/api/routes.py
 M tests/test_routes.py
```

### Step 2: Group Related Changes

Organize files into logical commit groups using these criteria:

**Grouping principles**:

| Criterion      | Example                              |
| -------------- | ------------------------------------ |
| **Directory**  | All `src/auth/` files together       |
| **Concern**    | Fix vs. Feature vs. Docs             |
| **Dependencies** | Files that import each other        |
| **Testing**    | Keep tests with source code          |

**Grouping example**:

Starting with mixed changes, group by concern:

```
Group 1: fix(auth)
- src/auth/login.py
- tests/test_login.py
Reason: Session timeout bug fix with tests

Group 2: feat(oauth)
- src/auth/oauth.py
- src/auth/providers/*.py
Reason: New OAuth2 feature (self-contained)

Group 3: docs(api)
- docs/CHANGELOG.md
- docs/API.md
Reason: Documentation updates

Group 4: fix(api)
- src/api/routes.py
- tests/test_routes.py
Reason: Bug fix in routing logic
```

**Special grouping cases**:

- **Tests with source**: Keep test files grouped with their source code
- **Infrastructure separate**: Build/CI changes in their own commit
- **Breaking changes isolated**: Put breaking changes in separate commit
- **Smaller is better**: Prefer 3-4 files per commit over 10+ files

### Step 3: Present Proposed Groups

Present each proposed commit clearly for user review:

```
Found 7 changes → 4 proposed commits

Commit #1: fix(auth) - Resolve session timeout on redirect
Files: src/auth/login.py, tests/test_login.py
Lines: +15, -8

Commit #2: feat(oauth) - Add OAuth2 support for Google and GitHub
Files: src/auth/oauth.py, src/auth/providers/google.py, src/auth/providers/github.py
Lines: +87, -3

Commit #3: docs(api) - Update API documentation
Files: docs/API.md, docs/CHANGELOG.md
Lines: +34, -2

Commit #4: fix(routes) - Fix race condition in request routing
Files: src/api/routes.py, tests/test_routes.py
Lines: +12, -5
```

### Step 4: Validate with User

Use AskUserQuestion to let the user review and adjust:

**Offer options**:
- ✓ **Proceed as suggested**: Accept all proposed groupings
- ✓ **Merge groups**: Combine related commits
- ✓ **Split a group**: Break one commit into multiple
- ✓ **Reorder commits**: Change commit sequence
- ✓ **Move files between groups**: Reorganize specific files

**Example adjustment**:
```
User response: "Merge commits #1 and #2 into one - they're both auth changes"

Revised plan:
Commit #1: feat(auth) - Add OAuth support and fix session timeout
Files: src/auth/login.py, src/auth/oauth.py, src/auth/providers/*, tests/test_*
Lines: +102, -11

Commit #2: docs(api) - Update API documentation
...
```

### Step 5: Commit Loop

For each group (in order):

#### 5.1 Stage Files

```bash
git add <file1> <file2> <file3>
```

Verify staging:
```bash
git diff --staged --stat
```

#### 5.2 Generate Commit Message

Analyze the staged changes to create a message following **Smart Commit** conventions:

**Subject line**:
- Type + optional scope + description
- Maximum 50 characters
- Imperative mood
- Example: `feat(oauth): add OAuth2 support for Google and GitHub`

**Body**:
- Explain WHAT and WHY
- Wrap at 72 characters
- Use bullet points for multiple aspects

**Footer**:
- Reference issues: `Closes #123`
- Co-author credit: `Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>`

**Example message**:
```
feat(oauth): add OAuth2 support for Google and GitHub

- Add provider abstraction for OAuth implementations
- Implement Google OAuth2 flow with email scope
- Implement GitHub OAuth2 flow with user:email scope
- Add token refresh mechanism for expired credentials
- Integrate with existing user session management

Results:
- Users can now sign in with Google or GitHub
- Automatic account linking for existing users
- Token expires and refreshes transparently

Closes #345
Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

#### 5.3 Execute Commit

If the user already approved the grouping in Step 4 and has not requested changes, proceed directly to commit without re-asking. Only show the generated message and ask for edit/skip if there is a specific reason to review message quality. The default is to proceed.

Use heredoc format for safe message passing:

```bash
git commit -m "$(cat <<'EOF'
feat(oauth): add OAuth2 support for Google and GitHub

- Add provider abstraction for OAuth implementations
- Implement Google OAuth2 flow with email scope
- Implement GitHub OAuth2 flow with user:email scope
- Add token refresh mechanism for expired credentials
- Integrate with existing user session management

Results:
- Users can now sign in with Google or GitHub
- Automatic account linking for existing users
- Token expires and refreshes transparently

Closes #345
Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

#### 5.4 Move to Next Group

Reset staging and proceed to next group:

```bash
git status  # Verify clean
# Stage next group's files
git add <next_files>
```

### Step 6: Summary

After all commits are processed, show a summary:

```
✓ Successfully created 4 commits:

a7f2c19 feat(oauth): add OAuth2 support for Google and GitHub
f8e1d2b fix(auth): resolve session timeout on redirect
c3b4a5e docs(api): update API documentation
d5c6e7f fix(routes): fix race condition in request routing

3 skipped groups:
- Group: chore(deps) - update dependencies
- Group: test(utils) - add utility tests

Final log (git log --oneline -n 4):
a7f2c19 feat(oauth): add OAuth2 support for Google and GitHub
f8e1d2b fix(auth): resolve session timeout on redirect
c3b4a5e docs(api): update API documentation
d5c6e7f fix(routes): fix race condition in request routing
```

## Commit Type Reference

Refer to the [Conventional Commits Reference](../git-commit/references/conventional-commits.md) for the full type table.

## Grouping Guidelines

### Do's

- ✓ **Keep related files together**: Feature code with its tests
- ✓ **Separate concerns**: Different features in different commits
- ✓ **Isolate breaking changes**: Put them in their own commit
- ✓ **Think about review**: Smaller commits are easier to review
- ✓ **Consider revert scenarios**: Can this commit be safely reverted?

### Don'ts

- ✗ **Don't mix features and fixes**: Create separate commits
- ✗ **Don't include unrelated refactoring**: Keep refactoring separate from feature work
- ✗ **Don't separate test from source**: Tests go with the code they test
- ✗ **Don't create monolithic commits**: Break large changes into logical chunks
- ✗ **Don't ignore infrastructure changes**: Build/CI changes need their own commits

## Edge Cases

### Single File Changes

If grouping reveals only one file changed:
```
You have only one file changed (src/utils/validation.py).
Consider using `/git-commit` directly for faster processing.
Proceed? [yes/no]
```

### All Changes Are Related

If all changes logically belong together:
```
All 7 file changes are part of the same feature (auth module).
Recommend single commit instead of multiple:

feat(auth): major refactor with new OAuth2 support
```

### Mixed Concerns in One File

When a single file has multiple unrelated concerns:
```
File src/auth/login.py contains changes for:
1. Session timeout fix (7 lines)
2. New OAuth integration (34 lines)

Consider using: git add -p
to split this file between commits manually.
```

### Deleted Files

When files are deleted:
```
Deleted files will be included in proposed groups.
Review carefully—sometimes deletions should be separate commits.

Example:
- Commit #1: feat(new-auth) - new authentication
- Commit #2: chore: remove legacy auth system
```

## Workflow Example

**Starting state**:
```
git status --short
 M src/auth/login.py
 M tests/test_auth.py
 M src/oauth/provider.py
?? src/oauth/google.py
?? src/oauth/github.py
 M src/api/routes.py
 M tests/test_routes.py
 M docs/CHANGELOG.md
 M config/version.txt
```

**Analysis and grouping**:
```
Commit #1: fix(auth) + feat(oauth)
→ Merged as single auth feature

Commit #2: fix(routes)
→ Separate concern

Commit #3: docs + version
→ Separate maintenance commit
```

**User confirms, wizard executes**:
1. Stage and commit auth changes
2. Stage and commit routes fix
3. Stage and commit docs/version
4. Show summary with 3 commits created

## Comparison with Smart Commit

Use **Commit Wizard** when:
- You have multiple uncommitted changes across different concerns
- You want help organizing them into logical commits
- You're preparing a clean history before pushing
- You need to split complex work into reviewable pieces

Use **`/git-commit`** when:
- You have a single, focused change
- All changes belong in one commit
- You just need fast message generation

## Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Write Good Commit Messages](https://chris.beams.io/posts/git-commit/)
- [Git Rebase Interactive for Organization](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History)
- [Atomic Commits](https://www.freshcodeblocks.com/articles/atomic-commits)

## Related Skills

- **`/git-commit`** — For single focused changes that are already staged
