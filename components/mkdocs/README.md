# mkdocs Component

Scaffolds a [MkDocs](https://www.mkdocs.org/) documentation site using the [Material theme](https://squidfunk.github.io/mkdocs-material/). Delivers a ready-to-serve config with dark/light mode, code highlighting, and API doc generation from docstrings.

## Files Delivered

| File                | Purpose                                               |
| ------------------- | ----------------------------------------------------- |
| `mkdocs.yml`        | Main config: theme, nav, plugins, markdown extensions |
| `docs/index.md`     | Home page stub                                        |
| `docs/api.md`       | API reference stub (rendered by mkdocstrings)         |
| `docs/changelog.md` | Changelog stub                                        |

## Quick Start

```bash
uv sync --group docs   # install docs dependencies
mkdocs serve           # live-reload dev server at http://localhost:8000
just docs-serve        # same, via just
mkdocs build           # build static site into site/
mkdocs gh-deploy       # deploy to GitHub Pages
```

## Template Variables

These values are substituted when the component is bootstrapped:

| Variable           | Controls                                          |
| ------------------ | ------------------------------------------------- |
| `{{project_name}}` | `site_name`                                       |
| `{{github_org}}`   | GitHub URLs, social links, copyright              |
| `{{repo_name}}`    | Repo URL, site URL, PyPI link                     |
| `{{description}}`  | `site_description`                                |
| `{{author}}`       | `site_author`, copyright                          |
| `{{package_name}}` | mkdocstrings source path (`src/{{package_name}}`) |

## Theme Features

- **Dark/light mode**: toggles via header button; respects system preference automatically
- **Material Design**: clean typography, responsive layout
- `navigation.tabs` — top-level nav rendered as tabs
- `navigation.top` — back-to-top button on scroll
- `search.highlight` — highlights search terms in results

## Plugins

| Plugin                        | Purpose                                                 |
| ----------------------------- | ------------------------------------------------------- |
| `search`                      | Full-text search (built-in)                             |
| `mkdocstrings[python]`        | Renders docstrings as API docs via `:::` directives     |
| `git-revision-date-localized` | Shows "Last updated" date on each page from git history |

## Adding Pages

Edit the `nav` block in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - API Reference: api.md
  - Changelog: changelog.md
  - Guide:
      - Installation: guide/install.md
      - Usage: guide/usage.md
```

Create the corresponding `.md` files under `docs/`. For API pages, use:

```markdown
# API Reference

::: mypackage.module
```

## Dependencies

Add to `pyproject.toml` docs group:

```toml
[dependency-groups]
docs = [
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.25",
    "mkdocs-git-revision-date-localized-plugin>=1.2",
]
```

## GitHub Pages Deployment

```bash
mkdocs gh-deploy
```

Builds the site and force-pushes to the `gh-pages` branch. Enable GitHub Pages in repo Settings → Pages → Source: `gh-pages` branch.

> Note: `site/` is generated locally and should be in `.gitignore`.
