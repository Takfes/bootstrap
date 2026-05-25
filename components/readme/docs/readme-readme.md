# readme

Installs a `README.md` in the project root with a standard GitHub project layout: title, description, badges, installation, quick start, development setup, and license.

---

## What Gets Installed

| File | Destination |
|------|-------------|
| `README.md` | Project root |

---

## Badges Included

| Badge | What it shows |
|-------|--------------|
| CI | GitHub Actions build status (`workflows/main.yml`) |
| Coverage | Codecov branch coverage |
| PyPI | Latest published version |
| Python | Supported Python versions |
| License | License type (auto-detected from `LICENSE` file) |

Badges link to the live GitHub Actions page, Codecov dashboard, and PyPI project page respectively. They will show "not found" states until the project is published and CI is wired up — replace or remove any that don't apply.

---

## Template Variables Used

| Variable | Example | Used in |
|----------|---------|---------|
| `{{project_name}}` | `my-project` | Title heading |
| `{{description}}` | `A fast data pipeline` | Subtitle |
| `{{github_org}}` | `acme-corp` | Badge URLs, clone URL |
| `{{repo_name}}` | `my-project` | Badge URLs, pip/uv install command |
| `{{package_name}}` | `my_project` | Python import example |
| `{{license_type}}` | `MIT` | License footer |
| `{{year}}` | `2026` | License footer |
| `{{author}}` | `Jane Smith` | License footer |

All variables are prompted during `bootstrap new` or `bootstrap add`.

---

## Sections

| Section | Purpose |
|---------|---------|
| Badges | At-a-glance project health |
| Installation | `pip install` and `uv add` commands |
| Quick Start | Minimal code example (placeholder — fill in after install) |
| Development | Clone, sync, pre-commit setup, common commands |
| Contributing | Fork → branch → commit → PR workflow |
| License | Type, year, and author |

The **Development → Common commands** section lists both `just` and `make` variants. Remove whichever task runner you did not install.

---

## Post-install checklist

After `bootstrap add readme`, fill in these before your first commit:

- [ ] Replace the `# TODO` comment in **Quick Start** with a real usage example
- [ ] Remove the `just` or `make` command table for whichever you didn't install
- [ ] Connect Codecov (or swap the coverage badge for `coveralls` / `shields.io/endpoint`)
- [ ] Confirm the CI badge points to your actual workflow filename

---

## Dependencies

None. Works standalone. The CI badge assumes a GitHub Actions workflow at `.github/workflows/main.yml` — add the `ci` component or update the badge URL if your workflow file is named differently.

## Usage

```
bootstrap add readme
```

If a `README.md` already exists it is skipped unless `--overwrite` is passed.
