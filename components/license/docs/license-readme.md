# license

Installs a `LICENSE` file in the root of the bootstrapped project.

## What Gets Installed

| File | Destination |
|------|-------------|
| `LICENSE` | Project root |

The license file is selected at install time based on the `license_type` variable
(prompted during `bootstrap new` / `bootstrap add`).

## Supported Licenses

| Key | License |
|-----|---------|
| `MIT` | MIT License (default) |
| `APACHE` | Apache License 2.0 |
| `BSD` | BSD 3-Clause License |
| `ISC` | ISC License |
| `GPL` | GNU General Public License v3 |

## Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{{author}}` | Prompted | `Your Name` |
| `{{year}}` | Auto (current year) | `2026` |
| `{{license_type}}` | Prompted | `MIT` |

MIT, BSD, and ISC licenses include `{{author}}` and `{{year}}` substitution.
Apache 2.0 and GPL v3 contain no user-specific placeholders.

## Dependencies

None.

## Usage

```
bootstrap add license
# Prompts: License type (MIT/Apache/BSD/ISC/GPL) [MIT]:
```

The selected license is written to `LICENSE` in the project root. If a `LICENSE`
file already exists it is skipped unless `--overwrite` is passed.
