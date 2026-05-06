# Conventional Commits Reference

## Commit Types

| Type       | When to use                  | Example                                    |
| ---------- | ---------------------------- | ------------------------------------------ |
| `feat`     | New feature                  | "add OAuth2 support"                       |
| `fix`      | Bug fix                      | "fix race condition in routing"            |
| `docs`     | Documentation only           | "update API documentation"                 |
| `style`    | Formatting, whitespace       | "format imports per eslint rules"          |
| `refactor` | Code restructuring           | "extract validation to utilities module"   |
| `perf`     | Performance improvement      | "optimize database queries"                |
| `test`     | Tests only                   | "add tests for user creation"              |
| `build`    | Build system                 | "upgrade React to 18.3"                    |
| `ci`       | CI/CD                        | "add GitHub Actions workflow"              |
| `chore`    | Maintenance                  | "update gitignore"                         |

## Selection Principle

Base the type on the **primary change intent**, not file count. If you changed 10 files but they're all part of one feature, it's still `feat`.

## Breaking Changes

Mark with `!` after the type: `feat(api)!: change endpoint format`

Always include a `BREAKING CHANGE:` footer with migration instructions.

## Specification

Full spec: https://www.conventionalcommits.org/
