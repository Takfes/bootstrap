# DevContainer: Reproducible Development Environment

A fully configured, reproducible development environment delivered as code. Open this repo in VSCode and you get an identical environment across your team — same Python version, same CLI tools, same Kubernetes access, same pre-commit hooks, same VSCode extensions — with zero manual setup. Also works as a GitHub Codespaces configuration.

---

## How It Works

### The Problem It Solves

Without a DevContainer, onboarding a new team member means: "Install Python 3.11, Homebrew, kubectl, Helm, the Azure CLI, pre-commit hooks, and make sure your kubeconfig points to the cluster." It usually goes wrong. Someone has Python 3.10, someone's on an older kubectl, dependencies are missing. The phrase "works on my machine" is code for "your environment is different."

A DevContainer eliminates this. It packages the entire toolchain into a container definition. VSCode detects it, builds the container, and your editor runs *inside* the container. You never run `python` on your host machine — you run it inside the container, which has the exact version and packages your team standardized on.

### How It Integrates with VSCode

1. You open the repo in VSCode
2. VSCode detects the `.devcontainer/` folder and prompts "Reopen in Container"
3. VSCode builds the Docker image defined in `.devcontainer/Dockerfile`
4. VSCode launches the container and installs a lightweight VS Code Server inside it
5. Your VS Code window reconnects — the editor looks the same, but the terminal, Python interpreter, debugger, and extensions are all running inside the container
6. Your repo files are mounted as a bind mount — edits in VS Code modify the real files on disk, git works normally

Everything that runs in a terminal (make, pytest, pre-commit, devspace, kubectl) runs inside the container. The heavy lifting happens there. Your host machine just provides the UI.

### Development Cycle with DevContainer

```
You edit code in VS Code (host or container — doesn't matter, same filesystem)
  ↓
Save file
  ↓
Terminal inside container runs `pytest` or `make dev`
  ↓
If using DevSpace: file syncs to your AKS pod (~1-2 seconds)
  ↓
If using mirrord: local process proxies calls through the pod
  ↓
See results in your terminal, fix bugs, repeat
```

For local development (editing, linting, testing), everything runs in the container. For cluster development, DevSpace deploys your code to a pod and syncs changes. For debugging, mirrord lets you run code locally but with the cluster's network context (database access, service URLs, environment variables). The DevContainer is the workbench; DevSpace/mirrord are the execution targets.

### What It Addresses

- **Consistency:** Every developer has identical tools, versions, and configurations
- **Onboarding:** New team member: clone repo, "Reopen in Container," 2 minutes of build time, fully productive
- **Portability:** Works on Mac, Windows, Linux — same container runs everywhere
- **Reproducibility:** Team can't drift into different tool versions or missing dependencies
- **CI/CD:** The same container that devs use locally can be committed to the repo and run in GitHub Actions or other CI pipelines

---

## Architecture Overview

Two files make a DevContainer work together:

### `.devcontainer/Dockerfile`

Defines the container image. This is a normal Dockerfile that starts from a base image (Microsoft's Ubuntu-based dev container base) and adds everything your team needs:

- Base OS tools (git, curl, etc.)
- CLI utilities (kubectl, helm, devspace, mirrord, k9s, uv, make, etc.)
- Language runtimes (Python, Node.js)
- DevContainer features (docker-in-docker, Azure CLI auto-login, etc.)
- Configuration files (copied from `assets/` folder)

When the container starts, all of this is already installed. Nothing is downloaded at runtime.

### `.devcontainer/devcontainer.json`

Configures how VSCode launches and manages the container. Specifies:

- Which Dockerfile to build
- Port mappings and environment variables
- What directories to mount from the host (e.g., `~/.kube`, `~/.azure`)
- Which VSCode extensions to auto-install
- Commands to run after the container starts (`postCreateCommand` — installs Python dependencies, sets up pre-commit hooks)
- Container resource limits
- VS Code settings

Think of it as the "contract between VSCode and Docker." The Dockerfile is the image; the `devcontainer.json` is how the image should be run.

---

## Tools Overview

| Group | Purpose | Key Tools | Details |
|-------|---------|-----------|---------|
| **CLI & Shell** | Command-line utilities, file handling, productivity | `make`, `just`, `fzf`, `jq`, `yq`, `ripgrep`, `lazygit` | See [devcontainer-tooling.md → CLI & Shell](./devcontainer-tooling.md#cli--shell-utilities) |
| **Kubernetes** | Cluster access, workload management, debugging | `kubectl`, `helm`, `k9s`, `devspace`, `mirrord`, `stern` | See [devcontainer-tooling.md → Kubernetes](./devcontainer-tooling.md#kubernetes-tools) |
| **Python** | Package management, virtual environments, execution | `uv` (package manager), Python 3.11, `pip` | See [devcontainer-tooling.md → Python](./devcontainer-tooling.md#python-tools) |
| **MCP Servers** | AI-assisted development, cluster queries, documentation | `context7`, `playwright`, `kubernetes-mcp`, `azure-devops-mcp` | See [devcontainer-tooling.md → MCP Servers](./devcontainer-tooling.md#mcp-servers) |
| **DevContainer Features** | Container capabilities, integrations | Docker socket mounting, Azure CLI, Node.js LTS | See [devcontainer-tooling.md → DevContainer Features](./devcontainer-tooling.md#devcontainer-features) |

For detailed tool descriptions, installation notes, and usage patterns, see [devcontainer-tooling.md](./devcontainer-tooling.md).

---

## Configuration & File Organization

### How Configuration Gets Injected

Files in `.devcontainer/assets/` are copied into the container during the build process and made available at runtime:

```
.devcontainer/
├── Dockerfile              # Build instructions
├── devcontainer.json       # VSCode/container config
└── assets/                 # Files injected into container at build time
    ├── shell_aliases.zsh   # Shell aliases (k=kubectl, d=devspace, etc.)
    ├── mcp_servers.json    # MCP server definitions
    └── settings.json       # VSCode workspace settings (.vscode/settings.json)
```

Each file is referenced in the Dockerfile via COPY instructions and positioned where it needs to be at runtime.

### MCP Servers

MCP servers enable AI tools (like Claude) to query your Kubernetes cluster, Azure resources, and documentation without leaving the editor. The `assets/mcp_servers.json` defines which servers are available:

- **kubernetes-mcp** — read-only access to cluster (pod status, logs, resource info)
- **azure-devops-mcp** — query pipelines, work items, repositories
- **context7** — fetch current documentation for libraries and frameworks
- **playwright** — web browsing and automation

See [devcontainer-tooling.md → MCP Servers](./devcontainer-tooling.md#mcp-servers) for details.

### Shell Aliases & Customization

The `assets/shell_aliases.zsh` file defines team-wide aliases that make common operations faster:

```bash
k=kubectl              # k get pods
kctx=kubectx           # context switching
kns=kubens             # namespace switching
d=devspace             # d dev (deploy locally)
dd="devspace dev"      # shorthand
py=ipython             # interactive Python
lg=lazygit             # git UI
```

These are sourced into the shell at container startup. Personal shell preferences (custom themes, additional aliases) can be mounted from the host if desired.

### VSCode Extensions

Extensions declared in `devcontainer.json` auto-install when the container builds. Team members all get:

- Python tooling (Pylance, Ruff, mypy)
- Kubernetes tools (kubectl extension, Docker)
- Git tools (GitLens, git-graph)
- Cloud tools (Azure CLI, mirrord)
- General productivity (YAML, TOML, spell checker)

Developers can add personal extensions on their host VSCode (themes, vim keybindings, etc.); these carry into the DevContainer automatically without needing to be declared.

---

## Mounts & Environment Setup

### Host Directories Mounted Into Container

The DevContainer binds select directories from your host into the container so that credentials and configs don't need to be duplicated or committed:

| Host Path | Container Path | Purpose |
|-----------|-----------------|---------|
| `~/.kube/` | `/home/vscode/.kube/` | Kubernetes config — `kubectl` and `k9s` use this to target your cluster |
| `~/.azure/` | `/home/vscode/.azure/` | Azure CLI credentials — `az` commands work without re-login |
| Docker socket | `/var/run/docker.sock` | Access to host's Docker daemon — `docker build` and DevSpace image builds use this |

These mounts are **bidirectional and transparent** — files are the same on both sides, not copied. When you run `az account show` in the container, it reads your actual Azure credentials from `~/.azure/`.

### Post-Create Setup

After the container starts, the `postCreateCommand` runs automatically:

```bash
uv sync && [ -f .pre-commit-config.yaml ] && pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg || true
```

This does two things:

1. **`uv sync`** — Installs your project's Python dependencies into `.venv/` (if a `pyproject.toml` exists)
2. **`pre-commit install`** — Registers Git hooks so that `pre-commit` runs automatically before commits (only if `.pre-commit-config.yaml` exists)

After this completes, commands like `uv run pytest`, `uv run ruff check .`, and pre-commit linting work immediately.

---

## Quick Start

### Opening in VSCode

1. **Install the Dev Containers extension** in VSCode if you don't have it
2. **Open the repo** in VSCode
3. You'll see a prompt: "Folder contains a Dev Container configuration file. Reopen folder to develop in a container?"
4. Click **"Reopen in Container"** (or press `Ctrl+Shift+P` and search "Dev Containers: Reopen in Container")
5. VSCode builds the container (2-5 minutes on first run) and reconnects
6. You're ready — open a terminal and start working

### Opening in GitHub Codespaces

1. On the repo's GitHub page, click **Code** → **Codespaces** → **Create codespace**
2. GitHub reads `.devcontainer/devcontainer.json` automatically and builds the environment in the cloud
3. You develop in VSCode in the browser with the same setup as local

### Verifying the Setup

Once the DevContainer is running, verify everything is in place:

```bash
# Check Python version and virtual environment
python --version
which python  # should be /workspace/.venv/bin/python

# Check Kubernetes access
kubectl get nodes  # connects to your configured cluster

# Check Git hooks
pre-commit run --all-files  # lints and formats your code
```

---

## Next Steps

For detailed information on each tool, usage patterns, and troubleshooting, see:

- **[devcontainer-tooling.md](./devcontainer-tooling.md)** — Full inventory of tools, installation details, and usage
