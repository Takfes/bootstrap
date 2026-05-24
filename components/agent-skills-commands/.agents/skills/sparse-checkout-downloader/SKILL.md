---
name: sparse-checkout-downloader
description: Use when downloading specific folders or files from a GitHub repository. Particularly useful when you want to clone only part of a large repo to save bandwidth and disk space. Include repository URL, target folder paths, and desired local destination.
---

# Sparse Checkout Downloader

Download specific folders or files from a Git repository without cloning the entire repository. This is useful for large monorepos or when you only need a subset of files.

## When to Use

- **Large repositories**: Clone only the folders you need instead of the entire repo
- **Monorepo subprojects**: Extract a single service, library, or component
- **Bandwidth constraints**: Minimize download size for specific directories
- **Partial updates**: Sync only changed folders to your local environment

**When NOT to use**: If you need the entire repository or multiple unrelated directories spread throughout the repo, a full clone is usually simpler.

## Core Concept

Git sparse checkout allows you to:
1. Initialize a repository with sparse patterns
2. Specify which folders/paths to actually download
3. Clone only those paths, avoiding unnecessary files

This is much faster than cloning everything then deleting what you don't need.

## Quick Reference

| Task | Command |
|------|---------|
| Clone single folder | `git clone --filter=blob:none --sparse <repo>`<br>`git sparse-checkout set <folder-path>` |
| Clone multiple folders | `git sparse-checkout set <path1> <path2> <path3>` |
| Clone with patterns | `git sparse-checkout set --no-cone <pattern>` |
| Add more folders later | `git sparse-checkout add <new-path>` |

## Implementation

### Basic sparse clone workflow:

```bash
# Initialize sparse clone
git clone --filter=blob:none --sparse <REPO_URL> <LOCAL_DIR>
cd <LOCAL_DIR>

# Configure which paths to download
git sparse-checkout set <FOLDER_PATH>

# If multiple folders needed:
git sparse-checkout set <FOLDER_1> <FOLDER_2> <FOLDER_3>

# Complete the setup
git checkout
```

### Example: Download only the `src/` folder from a repo

```bash
git clone --filter=blob:none --sparse https://github.com/user/myrepo.git myrepo
cd myrepo
git sparse-checkout set src
git checkout
```

### Example: Download multiple specific folders

```bash
git clone --filter=blob:none --sparse https://github.com/user/monorepo.git monorepo
cd monorepo
git sparse-checkout set services/auth docs/api-spec scripts/deploy
git checkout
```

## Key Flags Explained

- `--filter=blob:none` — Download commit history but not file contents upfront (lazy loading)
- `--sparse` — Start with no files checked out; you specify what to include
- `git sparse-checkout set` — Define which paths to checkout
- `--no-cone` — Allow glob patterns (e.g., `*.md` for all markdown files)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting `git checkout` after `sparse-checkout set` | Run `git checkout` to finalize |
| Wrong path format | Use repo-relative paths: `src/main` not `/src/main` |
| Setting paths before initializing | Always run `git clone --sparse` first |
| Using this for small repos | Full clone is simpler; sparse checkout shines with large repos (500MB+) |

## Real-World Impact

- **Bandwidth savings**: 90%+ reduction for large monorepos when cloning only one service
- **Setup time**: Faster initial clone and checkout compared to filtering after the fact
- **Disk usage**: Only store the folders you actually use

## Advanced: Adding paths later

After initial setup, add more folders without re-cloning:

```bash
git sparse-checkout add new/folder/path
git checkout
```

Or modify your sparse-checkout config directly:

```bash
# View current sparse-checkout configuration
cat .git/info/sparse-checkout

# Edit manually or via git command
git sparse-checkout set folder1 folder2 folder3
```

## Troubleshooting

**"sparse-checkout: pathspec did not match any files"**
- Verify the path exists in the repo (check GitHub web interface)
- Paths are case-sensitive

**"fatal: not a git repository"**
- Ensure you're inside the cloned directory
- Run from the root of the repo

**Slow performance on first checkout**
- This is normal for first `git checkout` after sparse-checkout set
- Subsequent operations are fast
