# mkdocs Component — Improvement Plan

## 1. Templatize All Project-Specific Values

The current `mkdocs.yml` hardcodes values from a specific project (`fun-quant-crypto-trade`, `Takfes`, `pytrade`). Every hardcoded value must be replaced with bootstrap template variables before this component can be used as a reusable scaffold.

| Field | Current value | Template variable |
|---|---|---|
| `site_name` | `fun-quant-crypto-trade` | `{{project_name}}` |
| `repo_url` | `https://github.com/Takfes/fun-quant-crypto-trade` | `https://github.com/{{github_org}}/{{repo_name}}` |
| `site_url` | `https://Takfes.github.io/fun-quant-crypto-trade` | `https://{{github_org}}.github.io/{{repo_name}}` |
| `site_description` | hardcoded string | `{{description}}` |
| `site_author` | `takis fessas` | `{{author}}` |
| `repo_name` | `Takfes/fun-quant-crypto-trade` | `{{github_org}}/{{repo_name}}` |
| `copyright` | hardcoded link to `Takfes.com` | `Maintained by <a href="https://github.com/{{github_org}}">{{author}}</a>.` |
| `mkdocstrings paths` | `["src/pytrade"]` | `["src/{{package_name}}"]` |
| Social GitHub link | `https://github.com/Takfes/fun-quant-crypto-trade` | `https://github.com/{{github_org}}/{{repo_name}}` |
| Social PyPI link | `https://pypi.org/project/fun-quant-crypto-trade` | `https://pypi.org/project/{{repo_name}}` |

**Action:** Run a find-and-replace pass on `mkdocs.yml` substituting all values above before committing the component.

---

## 2. Fix the `features` Key Structure

**Bug:** The current config uses:
```yaml
theme:
  feature:
    tabs: true
```
This is incorrect. The mkdocs-material theme uses a `features` list, not a nested `feature` map. The correct syntax is:

```yaml
theme:
  features:
    - navigation.tabs
    - navigation.top
    - search.highlight
    - search.suggest
```

**Action:** Replace `feature: tabs: true` with a proper `features` list. Add `navigation.top` (back-to-top button) and `search.highlight` while at it — both are zero-cost quality-of-life additions.

---

## 3. Expand the Default Nav Structure

The current nav only exposes `Home` and `Modules`. A more useful scaffold that new projects can extend:

```yaml
nav:
  - Home: index.md
  - API Reference: api.md
  - Changelog: changelog.md
```

`Modules` is vague and mkdocstrings-specific. `API Reference` is clearer. `Changelog` is a near-universal need.

**Action:** Replace the two-item nav with the three-item version above.

---

## 4. Add Missing Markdown Extensions

The material theme's most useful extensions are absent. Add at minimum:

```yaml
markdown_extensions:
  - toc:
      permalink: true
  - admonition
  - pymdownx.details
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.superfences
  - pymdownx.arithmatex:
      generic: true
  - attr_list
  - md_in_html
```

- `admonition` + `pymdownx.details`: enables callout boxes (`!!! note`, `??? warning`)
- `pymdownx.highlight` + `pymdownx.inlinehilite` + `pymdownx.superfences`: proper code block highlighting with line anchors
- `attr_list` + `md_in_html`: allows CSS classes on elements and raw HTML in markdown

**Action:** Add all six extensions above to `markdown_extensions`.

---

## 5. Add `git-revision-date-localized` Plugin

Shows a "Last updated" timestamp on each page sourced from git history. Minimal config:

```yaml
plugins:
  - search
  - git-revision-date-localized:
      enable_creation_date: true
  - mkdocstrings:
      handlers:
        python:
          paths: ["src/{{package_name}}"]
```

Requires `mkdocs-git-revision-date-localized-plugin` in the docs dependency group of `pyproject.toml`.

**Action:** Add plugin entry to `mkdocs.yml` and confirm the pyproject.toml docs group includes this package.

---

## 6. Ship a Minimal `docs/` Scaffold

The component currently delivers only `mkdocs.yml`. Running `mkdocs serve` immediately fails if `docs/index.md` does not exist. The component should ship:

```
docs/
├── index.md       # stub: # Project Name \n Welcome to the docs.
├── api.md         # stub: # API Reference \n ::: {{package_name}}
└── changelog.md   # stub: # Changelog \n _No entries yet._
```

**Action:** Add these three stub files to the component. They are placeholders — projects replace content after bootstrap.

---

## 7. Register Component in `manifest.toml`

The `mkdocs` component has no entry in `components/manifest.toml`. It must be registered so the bootstrap CLI knows it exists and can resolve its dependencies:

```toml
[mkdocs]
description = "MkDocs + Material theme documentation scaffold"
requires = ["uv"]
```

**Action:** Append this block to `components/manifest.toml`.

---

## 8. Gitignore the `site/` Directory

`mkdocs build` generates a `site/` directory at the repo root. This should be excluded from version control. Check whether the bootstrap base `.gitignore` already includes `site/`; if not, add it to the gitignore component or document it as a manual step.

**Action:** Confirm `site/` is in the base `.gitignore`. If not, add it.

---

## 9. Note on `edit_uri` Branch Name

`edit_uri: edit/main/docs/` hardcodes the `main` branch. This is correct for most projects but will silently produce broken edit links if the default branch is named differently (e.g. `master`). Add a comment in `mkdocs.yml` flagging this:

```yaml
edit_uri: edit/main/docs/  # Change 'main' if your default branch has a different name
```

**Action:** Add inline comment. No structural change needed.

---

## 10. Pin mkdocs-material Version

Ensure the docs dependency group in the pyproject.toml component pins mkdocs-material to a minimum version to prevent silent breakage from upstream changes:

```toml
[dependency-groups]
docs = [
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.25",
    "mkdocs-git-revision-date-localized-plugin>=1.2",
]
```

**Action:** Verify pins exist in the pyproject.toml component; add lower bounds if missing.
