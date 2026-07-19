# DevContainer + Cluster Development — Crash Course

## What the DevContainer Gives You

Opening this repo in VS Code with "Reopen in Container" gives you a fully configured workbench inside Docker. Pre-installed: Python (via uv), kubectl, helm, k9s, devspace, mirrord, lazygit, Azure CLI, Node.js, and a curated set of shell aliases. Your kubeconfig and Azure credentials mount from the host — no re-authentication inside the container.

The source code lives on your host filesystem and is bind-mounted into the container. Edits in VS Code modify the real files; git operations work normally. The container is the **runtime environment**, not the storage.

---

## Day-0 Setup

1. Clone the repo and open it in VS Code
2. Click **"Reopen in Container"** when prompted (or run `Dev Containers: Reopen in Container` from the command palette)
3. Wait for `postCreateCommand` to finish — this runs `uv sync` and installs pre-commit hooks
4. Verify cluster access: `kubectl config get-contexts`
5. Switch context if needed: `kctx` (interactive picker) or `kubectl config use-context <name>`

---

## Two Inner-Loop Development Modes

### DevSpace — run your code in the cluster

`devspace dev` builds your image, deploys a dev pod in the cluster, and syncs local file changes to the pod in real time. Frameworks that support hot-reload (uvicorn `--reload`, nodemon) pick up changes within seconds — no commit, no pipeline, no redeployment.

```bash
dd          # devspace dev — deploy and start sync
ds          # devspace status — check active session
```

DevSpace reads `devspace.yaml` from the repo root for build, sync, and port-forward configuration.

**Best for:** services that need cluster compute or network, or when you want the full in-cluster runtime environment.

### mirrord — run locally with cluster context

`mirrord exec -t deployment/<name> -- <command>` intercepts your local process at the OS level and proxies network calls, environment variables, and filesystem reads through a lightweight agent in the target pod. Your local Python process sees the cluster's DB credentials, internal service DNS, and whitelisted network as if it were inside the pod.

```bash
dm exec -t deployment/my-service -- python src/worker.py
```

No deployment required — mirrord attaches to an existing workload. Use traffic mirroring to leave the live pod running while your local process receives a copy of its traffic.

**Best for:** debugging with VS Code breakpoints, one-off scripts against live cluster state, testing against whitelisted databases without a full pod deployment.

---

## Key Aliases

| Alias | Expands to |
|-------|-----------|
| `k` | `kubectl` |
| `kctx` | `kubectx` — interactive context switcher |
| `kns` | `kubens` — interactive namespace switcher |
| `kcl` | `kubectl config get-contexts` |
| `kl` | `kubectl logs` |
| `klf` | `kubectl logs --follow` |
| `dd` | `devspace dev` |
| `ds` | `devspace status` |
| `dm` | `mirrord` |
| `lg` | `lazygit` |

Full alias reference: `.devcontainer/assets/shell_aliases.zsh`

---

## Important Notes

- **Credentials** — `.kube/` and `.azure/` are bind-mounted from the host. No credentials are stored in the image.
- **Docker access** — the `docker-outside-of-docker` feature gives the container access to the host Docker daemon. `docker build` runs on the host, not inside the container.
- **Dependency changes** — `uv add <package>` inside the container writes `uv.lock` to the bind-mounted filesystem (visible on the host immediately). If packages change frequently during a DevSpace session, run `uv sync` inside the dev pod manually or add a file-watch hook in `devspace.yaml`.
