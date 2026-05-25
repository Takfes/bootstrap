# DevContainer Tooling Reference

Detailed inventory of all tools installed in the DevContainer, how they're installed, and how to use them.

---

## CLI & Shell Utilities

Essential command-line tools for productivity, file handling, and general shell operations.

### make

**Purpose:** Task automation and project orchestration  
**Installed via:** `apt-get`  
**Version:** Latest from Ubuntu 24.04 repos

Run predefined tasks by typing `make <target>`. Common targets in this project:

```bash
make dev              # Start development environment (DevSpace or mirrord)
make test             # Run pytest
make lint             # Run Ruff linter
make format           # Format code with Ruff
```

See the `Makefile` in your project root for available targets.

**Docs:** https://www.gnu.org/software/make/manual/

### just

**Purpose:** Modern alternative to make, simpler syntax  
**Installed via:** `apt-get`  
**Version:** Latest from Ubuntu 24.04 repos

Like `make` but with cleaner syntax. If your project uses a `justfile`:

```bash
just dev              # Same as make dev, but cleaner
just test
```

**Docs:** https://github.com/casey/just

### fzf

**Purpose:** Fuzzy file finder — fast, interactive file/command search  
**Installed via:** `apt-get`  
**Version:** Latest

Integrated into shell history and file search. Press `Ctrl+R` to fuzzily search bash history:

```bash
Ctrl+R                # Search shell history interactively
cd <directory> && Ctrl+T  # Fuzzily search files to insert into command
```

**Docs:** https://github.com/junegunn/fzf

### jq

**Purpose:** JSON query and formatting  
**Installed via:** `apt-get`  
**Version:** Latest

Parse and transform JSON from the command line:

```bash
kubectl get pods -o json | jq '.items[].metadata.name'
curl https://api.example.com/data | jq '.results[] | select(.status == "active")'
```

**Docs:** https://stedolan.github.io/jq/

### yq

**Purpose:** YAML query and formatting (like jq but for YAML)  
**Installed via:** `apt-get`  
**Version:** Latest

Parse and transform YAML:

```bash
yq eval '.spec.containers[0].image' deployment.yaml
yq eval '.metadata.labels.app = "myapp"' -i deployment.yaml
```

**Docs:** https://github.com/mikefarah/yq

### ripgrep (rg)

**Purpose:** Fast recursive file search  
**Installed via:** `apt-get`  
**Version:** Latest

Search files much faster than grep:

```bash
rg "TODO" src/          # Find all TODOs in src/
rg "def query_db" --type py  # Search Python files for function definition
```

**Docs:** https://github.com/BurntSushi/ripgrep

### lazygit

**Purpose:** Interactive Git TUI (terminal user interface)  
**Installed via:** Direct binary download  
**Version:** Latest stable

Visual Git workflow without touching the CLI:

```bash
lazygit                # Opens interactive UI for staging, committing, branching
lg                     # Alias: lg = lazygit
```

**Docs:** https://github.com/jesseduffield/lazygit

### zoxide

**Purpose:** Smarter `cd` command — jump to directories by name  
**Installed via:** `apt-get`  
**Version:** Latest

Learning directory jumper:

```bash
cd /home/user/projects/data-pipeline
z data                 # Next time, just type 'z data' and you jump there
z -                    # Jump to previous directory
```

**Docs:** https://github.com/ajeetdsouza/zoxide

### bat

**Purpose:** Syntax-highlighted cat replacement  
**Installed via:** `apt-get`  
**Version:** Latest

Like `cat` but with colors and Git integration:

```bash
bat Dockerfile         # Colored syntax highlighting
git diff | bat         # Pipe diff output for readability
```

**Docs:** https://github.com/sharkdp/bat

### fd

**Purpose:** User-friendly alternative to `find`  
**Installed via:** `apt-get`  
**Version:** Latest

Simpler and faster than find:

```bash
fd '\.py$' src/        # Find all Python files in src/
fd test --type f       # Find all files named 'test'
```

**Docs:** https://github.com/sharkdp/fd

### git-delta

**Purpose:** Syntax-highlighted Git diff viewer  
**Installed via:** `apt-get`  
**Version:** Latest

Configure Git to use delta for all diffs (already set up in `.gitconfig` if included):

```bash
git diff              # Automatically shown with colors and side-by-side
git log -p            # Patch view also uses delta
```

**Docs:** https://github.com/dandavison/delta

### duf

**Purpose:** Disk usage analyzer — prettier `df`  
**Installed via:** `apt-get`  
**Version:** Latest

See disk space usage in a readable format:

```bash
duf                   # Shows mounted filesystems and usage
duf /home/vscode      # Check workspace directory size
```

**Docs:** https://github.com/muesli/duf

### gping

**Purpose:** Visual ping — animated ping with graphs  
**Installed via:** `apt-get`  
**Version:** Latest

Ping with a nice visual output:

```bash
gping kubernetes.default.svc.cluster.local  # Check cluster service connectivity
```

**Docs:** https://github.com/orf/gping

---

## Kubernetes Tools

Cluster management, debugging, and development tools for Kubernetes.

### kubectl

**Purpose:** Kubernetes command-line interface  
**Installed via:** `devcontainers/kubectl-helm-minikube` feature  
**Version:** Latest stable

Query and manage your Kubernetes cluster:

```bash
kubectl get pods -n my-namespace           # List pods
kubectl describe pod my-pod                # Inspect pod details
kubectl logs -f my-pod                     # Stream pod logs
kubectl port-forward svc/my-service 8080:8080  # Forward port locally
kubectl exec -it my-pod -- /bin/bash       # Shell into pod
```

The container has your `~/.kube/config` mounted, so kubectl connects to your actual cluster without any additional setup.

**Docs:** https://kubernetes.io/docs/reference/kubectl/

**Team alias:** `k=kubectl`

### helm

**Purpose:** Kubernetes package manager  
**Installed via:** `devcontainers/kubectl-helm-minikube` feature  
**Version:** Latest stable

Deploy and manage applications via Helm charts:

```bash
helm repo add myrepo https://charts.example.com
helm install my-release myrepo/mychart
helm upgrade my-release myrepo/mychart --values values.yaml
helm status my-release
```

**Docs:** https://helm.sh/docs/

### k9s

**Purpose:** Interactive terminal UI for Kubernetes  
**Installed via:** Direct binary download  
**Version:** Latest stable

A visual, real-time Kubernetes dashboard in your terminal:

```bash
k9s                   # Opens interactive UI
# Inside k9s:
# - Type ':pods' to view pods
# - Type ':deploy' to view deployments
# - Press 'l' on a pod to see logs
# - Press 'e' to edit a resource
# - Type '/search-term' to filter
```

Navigate using arrow keys, search with `/`, execute actions with single keypresses. Much faster than `kubectl` for visual inspection and quick actions.

**Docs:** https://k9scli.io/

### devspace

**Purpose:** Inner loop development — sync code to cluster and hot-reload  
**Installed via:** Direct binary download  
**Version:** Latest stable

Deploy your code to a Kubernetes pod with file sync, hot-reload, and interactive terminal. Instead of commit → push → pipeline → wait → test, you get: save → sync (1-2 seconds) → test.

```bash
devspace dev          # Start dev mode: deploy pod, sync files, open shell
# Inside the DevSpace shell:
python main.py        # Your code runs in the cluster with synced files
# Save code in VS Code → file syncs instantly → app hot-reloads (if configured)
```

**How it works:**
1. DevSpace builds your app's Docker image and deploys a pod to your cluster
2. It overrides the pod's entrypoint with a shell
3. It sets up bidirectional file sync between your local code and the pod
4. You run your app manually in the pod's terminal
5. Every file save locally syncs to the pod (~1-2 seconds)

**Why use it:** Testing code against real cluster services (database, message queues, other microservices) without deploying through a full pipeline. Feedback loop drops from 10+ minutes to seconds.

**Docs:** https://devspace.sh/docs

**Team alias:** `d=devspace`, `dd="devspace dev"`

### mirrord

**Purpose:** Debug code locally while connected to the cluster  
**Installed via:** Direct binary download via mirrord CLI  
**Version:** Latest stable

Run code on your laptop but make it "think" it's in the cluster. Network calls, environment variables, file reads — all proxied through a target pod.

```bash
mirrord exec -t deployment/my-app -- python -m debugpy --listen 5678 src/main.py
# Now your local Python process inherits the pod's:
# - Environment variables (DB credentials, config)
# - Network (can reach cluster services, whitelisted databases)

# Then connect VS Code's debugger to localhost:5678
```

**Why use it:** Debugging. When you hit a bug and need to set a breakpoint, inspect the call stack, and step through code, debugging in a remote pod is painful. mirrord lets you use VS Code's full debugger locally while your code sees the cluster's network and configs.

**Docs:** https://mirrord.dev/

### stern

**Purpose:** Multi-pod log tailing  
**Installed via:** Direct binary download  
**Version:** Latest stable

Tail logs from multiple pods at once with filtering:

```bash
stern my-app          # Follow logs from all pods matching 'my-app'
stern -n kube-system --tail 50 coredns  # Last 50 lines from coredns pods
stern -c my-container my-app  # Only logs from specific container
```

Much faster than multiple `kubectl logs -f` commands.

**Docs:** https://github.com/stern/stern

### kubectx / kubens

**Purpose:** Quick context and namespace switching  
**Installed via:** Direct binary downloads  
**Version:** Latest stable

Switch between clusters and namespaces without typing the full kubectl command:

```bash
kubectx                 # List available contexts
kubectx prod            # Switch to 'prod' context
kubens my-namespace     # Switch to namespace
kubens -                # Switch back to previous namespace
```

**Team aliases:** `kctx=kubectx`, `kns=kubens`

**Docs:** https://github.com/ahmetb/kubectx

---

## Python Tools

Python runtime, package management, and development utilities.

### Python 3.11

**Purpose:** Language runtime  
**Installed via:** `devcontainers/python` feature  
**Version:** 3.11.x (pinned in Dockerfile)

The Python executable used by all tools. Your code runs on this version.

```bash
python --version       # Verify version
python -c "import sys; print(sys.prefix)"  # Shows venv location
```

Ensure your `pyproject.toml` specifies compatible versions:

```toml
[project]
requires-python = ">=3.11"
```

### uv

**Purpose:** Ultra-fast Python package manager and virtual environment manager  
**Installed via:** Pre-built binary from `ghcr.io/astral-sh/uv`  
**Version:** Pinned (see Dockerfile)

Modern replacement for pip + virtualenv. Dramatically faster and more reliable.

```bash
uv sync               # Install dependencies from pyproject.toml into .venv/
uv run pytest         # Run command in the virtual environment
uv add requests       # Add a new dependency
uv remove requests    # Remove a dependency
uv lock               # Generate uv.lock (like package-lock.json)
```

All dependencies should be declared in `pyproject.toml`. The `postCreateCommand` runs `uv sync` automatically, so `.venv/` is populated before you open a terminal.

**Docs:** https://docs.astral.sh/uv/

---

## MCP Servers

AI-assisted development tools that run locally in the container and provide domain-specific context to AI assistants.

### kubernetes-mcp

**Purpose:** Read-only Kubernetes cluster introspection  
**Installed via:** Direct binary (Go-based implementation)

Exposes Kubernetes cluster state as an MCP server. Any AI tool configured to use it can query pods, deployments, services, logs, resource status — all without leaving the editor.

**Configuration:** Declared in `assets/mcp_servers.json`

**Docs:** https://github.com/containers/kubernetes-mcp-server

**Security note:** Read-only by design. Use a service account with minimal permissions:
```bash
kubectl create serviceaccount mcp-reader
kubectl create clusterrolebinding mcp-reader --clusterrole=view --serviceaccount=default:mcp-reader
```

### context7

**Purpose:** Fetch up-to-date documentation for libraries, frameworks, and APIs  
**Installed via:** `npx` (on-demand, requires Node.js)  
**Transport:** stdio

Queries documentation without your AI assistant's knowledge cutoff. Ask Claude "How do I use the latest React hooks?" and it fetches current React docs automatically.

**Docs:** https://github.com/upstash/context7

### playwright

**Purpose:** Web automation and browser control  
**Installed via:** `npx` (on-demand, requires Node.js)  
**Transport:** stdio

Enables AI tools to control a browser for web scraping, form filling, testing.

**Docs:** https://playwright.dev/

### sequential-thinking

**Purpose:** Step-by-step reasoning scaffold for complex tasks  
**Installed via:** `npx` (on-demand)  
**Transport:** stdio

Guides AI assistants through multi-step problems with explicit reasoning chains.

**Docs:** https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking

### Tavily (Remote MCP)

**Purpose:** Real-time web search  
**Transport:** HTTP (remote)  
**Requires:** `TAVILY_API_KEY` environment variable

Provides web search capability to AI tools within the container. Configure your API key:

```bash
export TAVILY_API_KEY="your-key-here"
```

**Docs:** https://tavily.com/

---

## DevContainer Features

Special capabilities and integrations provided by the DevContainers feature system.

### Docker Socket Mounting

**Purpose:** Access to host's Docker daemon for builds  
**Configuration:** In `devcontainer.json` mounts section

Mounts `/var/run/docker.sock` from the host into the container. This lets `docker` and `devspace` commands inside the container use the host's Docker daemon.

**Why:** Avoids Docker-in-Docker (DinD) overhead. When you run `docker build` in the container, it actually executes on the host's Docker, keeping builds fast.

**Trade-off:** The container has full access to the host's Docker (could start/stop other containers). For a dev environment, this is acceptable. For multi-tenant or security-sensitive setups, consider DinD with rootless mode instead.

### Node.js LTS

**Purpose:** JavaScript runtime for MCP servers and build tools  
**Installed via:** `devcontainers/node` feature  
**Version:** Latest LTS

Used for running MCP servers via `npx` (context7, playwright, sequential-thinking).

```bash
node --version
npx some-tool          # Run tools without installing globally
```

### Azure CLI

**Purpose:** Authenticated access to Azure resources  
**Installed via:** `devcontainers/azure-cli` feature  
**Version:** Latest

Pre-configured with your host's Azure credentials (mounted from `~/.azure/`). Run Azure commands without re-login:

```bash
az account show        # Check current Azure account
az aks get-credentials --resource-group my-rg --name my-aks  # Get cluster kubeconfig
az acr login -n my-acr.azurecr.io  # Login to container registry
```

### kubectl + helm + minikube

**Purpose:** Kubernetes toolchain  
**Installed via:** `devcontainers/kubectl-helm-minikube` feature  
**Version:** Latest stable for each tool

Pre-installed versions of kubectl, helm, and minikube for local Kubernetes testing.

```bash
minikube start --cpus=2 --memory=4096  # Start local cluster
kubectl config use-context minikube    # Switch to minikube
```

---

## Assets Folder

Configuration files that get injected into the container at build time. Located in `.devcontainer/assets/`:

### shell_aliases.zsh

Shell aliases for common operations. Sourced into `.bashrc` and `.zshrc` during container build. Covers Kubernetes, DevSpace, Docker, Git, Python, and shell utilities. See inline comments for usage.

### mcp_servers.json

MCP server definitions. Tells Claude Code and other AI tools which MCP servers are available and how to reach them. Copied into `/home/vscode/.config/mcp/` during image build.

### settings.json

VSCode workspace settings. Contains Python formatter config, Ruff integration, Jupyter settings, and MCP discovery preferences. Installed as `.vscode/settings.json` in the bootstrapped project.

---

## Troubleshooting & Common Questions

**Q: Which Python should I use — container's or host's?**  
A: Always the container's. Use `uv run` or activate `.venv/` with `source .venv/bin/activate`.

**Q: How do I add a new tool to the DevContainer?**  
A: Edit `.devcontainer/Dockerfile`, add a `RUN apt-get install` or download line, rebuild the container (VSCode will prompt). Commit the change so the team rebuilds on next pull.

**Q: Can I use the DevContainer with Jupyter?**  
A: Yes. Install Jupyter in `pyproject.toml` dependencies, then `uv run jupyter notebook`. VSCode will detect the server and offer to open it in the browser locally.

**Q: How do I update MCP servers?**  
A: If they're npm-based (context7, playwright), `npx` automatically uses the latest. For binary-based servers, update the Dockerfile and rebuild.
