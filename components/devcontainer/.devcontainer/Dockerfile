FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# 1. Base Unix Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    fzf zoxide jq yq bat fd-find ripgrep httpie git-delta duf gping \
    make just git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/batcat /usr/local/bin/bat \
    && ln -s /usr/bin/fdfind /usr/local/bin/fd

# 2. UV — pinned for reproducibility; increment deliberately when upgrading
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

# 3. Architecture-aware binary downloads (k9s, stern, devspace, lazygit)
RUN set -eux; \
    ARCH=$(uname -m); \
    case "$ARCH" in \
      x86_64)  ARCH_K9S="amd64"; ARCH_LG="x86_64"; ARCH_DS="amd64" ;; \
      aarch64) ARCH_K9S="arm64"; ARCH_LG="arm64";  ARCH_DS="arm64"  ;; \
      *) echo "Unsupported architecture: $ARCH" && exit 1 ;; \
    esac; \
    \
    # k9s
    curl -fsSL "https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_${ARCH_K9S}.tar.gz" \
      | tar xz -C /usr/local/bin k9s; \
    \
    # stern
    STERN_VER=$(curl -fsSL https://api.github.com/repos/stern/stern/releases/latest | jq -r .tag_name); \
    curl -fsSL "https://github.com/stern/stern/releases/download/${STERN_VER}/stern_${STERN_VER#v}_linux_${ARCH_K9S}.tar.gz" \
      | tar xz -C /usr/local/bin stern; \
    \
    # devspace
    curl -fsSL "https://github.com/loft-sh/devspace/releases/latest/download/devspace-linux-${ARCH_DS}" \
      -o /usr/local/bin/devspace && chmod +x /usr/local/bin/devspace; \
    \
    # lazygit
    LG_VER=$(curl -fsSL "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | jq -r '.tag_name | ltrimstr("v")'); \
    curl -fsSL "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LG_VER}_Linux_${ARCH_LG}.tar.gz" \
      | tar xz -C /usr/local/bin lazygit

# 4. kubectx & kubens
RUN git clone --depth=1 https://github.com/ahmetb/kubectx /opt/kubectx \
    && ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx \
    && ln -s /opt/kubectx/kubens /usr/local/bin/kubens

USER vscode

# 5. Shell customisation
COPY assets/shell_aliases.zsh /home/vscode/.shell_aliases.zsh
RUN echo 'source ~/.shell_aliases.zsh' >> ~/.bashrc \
    && echo 'source ~/.shell_aliases.zsh' >> ~/.zshrc \
    && echo 'eval "$(zoxide init bash)"' >> ~/.bashrc \
    && echo 'eval "$(zoxide init zsh)"' >> ~/.zshrc
