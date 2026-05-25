#!/usr/bin/env zsh
# DevContainer shell aliases — sourced from ~/.bashrc and ~/.zshrc on container startup.
# Sections: Kubernetes | DevSpace & Mirrord | Docker | Git | Python | Productivity | Functions

# ==============================================================
# > Kubernetes & Cluster
# ==============================================================

alias k='kubectl'                            # k get pods
alias kg='kubectl get'                       # kg pods -n <namespace>
alias kga='kubectl get --all-namespaces all' # all resources across all namespaces
alias kd='kubectl describe'                  # kd pod <name>
alias kaf='kubectl apply -f'                 # kaf manifest.yaml
alias kex='kubectl exec -it'                 # kex <pod> -- bash
alias ke='kubectl explain'                   # ke pod.spec.containers
alias kar='kubectl api-resources'            # list all available API resource types
alias kcl='kubectl config get-contexts'      # list all available contexts
alias kcc='kubectl config current-context'   # show the active context
alias kl='kubectl logs'                      # kl <pod>
alias klf='kubectl logs --follow'            # klf <pod> — stream logs in real-time
alias kctx='kubectx'                         # kctx <context> — switch cluster context
alias kns='kubens'                           # kns <namespace> — switch namespace

# ==============================================================
# > DevSpace & Mirrord
# ==============================================================

alias d='devspace'                           # d dev — deploy and start inner-loop dev
alias dd='devspace dev'                      # dd — shorthand
alias ds='devspace status'                   # ds — check active devspace status
alias dm='mirrord'                           # dm exec -t deployment/<name> -- <cmd>

# ==============================================================
# > Docker
# ==============================================================

alias dfi='docker search'                    # search Docker Hub for images
alias dfio='docker search --filter is-official=true'  # official images only
alias dpl='docker pull'                      # dpl <image:tag>
alias db='docker build -t'                   # db <name:tag> .
alias di='docker image ls'                   # list all images
alias dv='docker volume ls'                  # list all volumes
alias dp="docker ps -a --format 'table {{.Names}}\t{{.ID}}\t{{.Image}}\t{{.Status}}'"  # formatted container list
alias dps='docker ps -a'                     # full container list (default format)
alias dn='docker network ls'                 # list networks
alias dsys='docker system df'                # disk usage summary
alias drm='docker rm'                        # drm <container>
alias drmi='docker rmi'                      # drmi <image>
alias drmv='docker volume prune'             # remove unused volumes
alias drmsys='docker system prune -a'        # full cleanup: containers, images, volumes
alias drun='docker run -dit'                 # drun <image> — detached + interactive
alias dstop='docker stop'                    # dstop <container>
alias dsa='docker stop $(docker ps -q)'      # stop all running containers
alias dex='docker exec -it'                  # dex <container> bash
alias dl='docker logs'                       # dl <container>
alias dlf='docker logs -f'                   # dlf <container> — follow logs
alias dc='docker compose'                    # dc up -d
alias dcp='docker compose ps'                # list compose services
alias dcl='docker compose logs'              # logs from all services
alias dcu='docker compose up -d'             # start services detached
alias dcd='docker compose down'              # stop and remove containers + networks
alias dcs='docker compose stop'              # stop without removing
alias dcr='docker compose restart'           # restart services

# ==============================================================
# > Git
# ==============================================================

alias gs='git status'                        # show working tree status
alias gca='git commit --amend'               # amend previous commit
alias gps='git push'                         # push commits to remote
alias gpl='git pull'                         # fetch and merge from remote
alias gfa='git fetch --all'                  # fetch all remotes
alias gcb='git checkout -b'                  # gcb <branch> — create and switch
alias gsw='git switch'                       # gsw <branch> — switch (modern)
alias gf='git checkout $(git branch | fzf)'  # interactive branch picker (fzf)
alias gb='git branch'                        # list local branches
alias gba='git branch -a'                    # list all branches (local + remote)
alias gbr='git branch -r'                    # list remote-tracking branches
alias gbn='git branch -m'                    # rename current branch
alias gbd='git branch -d'                    # delete branch (safe)
alias gbD='git branch -D'                    # delete branch (force)
alias gbdr='git push origin --delete'        # delete remote branch
alias grml='git remote -v'                   # list remotes with URLs
alias grma='git remote add'                  # grma <name> <url>
alias grmr='git remote remove'               # grmr <name>
alias gt='git stash'                         # save current changes to stash
alias gtl='git stash list'                   # list all stashes
alias gta='git stash apply'                  # apply stash without removing it
alias gtp='git stash pop'                    # apply and remove most recent stash
alias gtd='git stash drop'                   # delete a stash entry
alias gtc='git stash clear'                  # remove all stash entries
alias gla="git log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"  # decorated log with authors
alias glb='git log --oneline --decorate --graph'       # compact one-line log
alias glc='git log --decorate --graph --oneline --all' # all branches one-line log
alias gdf='git diff'                         # show unstaged changes
alias gds='git diff --staged'                # show staged changes
alias gdh='git diff HEAD'                    # show all changes since HEAD
alias gdm='git diff --name-only --diff-filter=U'  # files with merge conflicts
alias grmc='git rm -r --cached'              # untrack files (keep on disk)
alias gfp='git fetch --all --prune'          # fetch + prune stale remote refs
alias lg='lazygit'                           # interactive Git TUI

# ==============================================================
# > Python & Environment
# ==============================================================

alias py='ipython'                           # interactive Python shell
alias activate='source .venv/bin/activate'  # activate project virtualenv

# ==============================================================
# > Productivity
# ==============================================================

alias ll='ls -lah'                           # long listing with hidden files
alias hist='history'                         # full shell history
alias c='clear'                              # clear terminal

# ==============================================================
# > Functions
# ==============================================================

# Checkout a remote branch as a local tracked branch
gbt() {
  git checkout -b "$1" "origin/$1"
}

# Remove all stopped containers
drma() {
  local stopped
  stopped=$(docker ps -a -q --filter status=exited)
  if [ -n "$stopped" ]; then
    docker rm $stopped
  else
    echo "No stopped containers."
  fi
}

# List all containers with their internal IP addresses
dip() {
  docker inspect \
    --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
    $(docker ps -aq)
}

# Interactive Kubernetes context switcher
kcx() {
  local contexts
  contexts=($(kubectl config get-contexts -o name))
  [ ${#contexts[@]} -eq 0 ] && echo "No contexts found." && return 1
  echo "Available contexts:"
  for i in "${!contexts[@]}"; do echo "  $((i+1)). ${contexts[$i]}"; done
  read -p "Select (0 to exit): " choice
  [ "$choice" -eq 0 ] && return 0
  kubectl config use-context "${contexts[$((choice-1))]}"
}

# Interactive Kubernetes namespace switcher
knsw() {
  local ctx namespaces
  ctx=$(kubectl config current-context)
  [ -z "$ctx" ] && echo "No current context set." && return 1
  namespaces=($(kubectl get namespaces -o custom-columns=NAME:.metadata.name --no-headers))
  [ ${#namespaces[@]} -eq 0 ] && echo "No namespaces found." && return 1
  echo "Namespaces in context '$ctx':"
  for i in "${!namespaces[@]}"; do echo "  $((i+1)). ${namespaces[$i]}"; done
  read -p "Select (0 to exit): " choice
  [ "$choice" -eq 0 ] && return 0
  kubectl config set-context "$ctx" --namespace="${namespaces[$((choice-1))]}"
  echo "Switched to namespace '${namespaces[$((choice-1))]}'"
}

# Create a directory and cd into it
mkcd() { mkdir -p "$1" && cd "$1"; }

# Remove Python cache and common cruft from a directory
clean() {
  local dir="${1:-.}"
  [ ! -d "$dir" ] && echo "Directory '$dir' not found." && return 1
  find "$dir" -type d \( -name '__pycache__' -o -name '.ruff_cache' -o -name '.ipynb_checkpoints' -o -name 'catboost_info' \) \
    -print -exec rm -rf {} + 2>/dev/null
  find "$dir" -type f -name '.DS_Store' -print -exec rm -f {} + 2>/dev/null
  echo "Cleaned '$dir'"
}

# Print system info summary
oinfo() {
  echo "System:    $(uname -s) $(uname -r)"
  echo "User:      $(whoami)@$(hostname)"
  echo "Shell:     $SHELL"
  command -v lsb_release &>/dev/null && echo "OS:        $(lsb_release -ds)"
}

# Show local and external network addresses
ninfo() {
  echo "Network interfaces:"
  if command -v ip &>/dev/null; then
    ip -o -4 addr show | awk '{print "  " $2 ": " $4}'
  elif command -v ifconfig &>/dev/null; then
    ifconfig | awk '/flags=/{iface=$1} /inet /{print "  " iface ": " $2}'
  fi
  echo "External IP:"
  command -v curl &>/dev/null && echo "  $(curl -s https://ifconfig.me)" || echo "  curl not available"
}

# Extract common archive formats
extract() {
  [ -z "$1" ] && echo "Usage: extract <archive>" && return 1
  if [ -f "$1" ]; then
    case "$1" in
      *.tar.xz)  tar -xvf "$1"   ;;
      *.tar.bz2) tar -jxvf "$1"  ;;
      *.tar.gz)  tar -zxvf "$1"  ;;
      *.tar)     tar -xvf "$1"   ;;
      *.tgz)     tar -zxvf "$1"  ;;
      *.bz2)     bunzip2 "$1"    ;;
      *.gz)      gunzip "$1"     ;;
      *.zip)     unzip "$1"      ;;
      *.rar)     7z x "$1"       ;;
      *.7z)      7z x "$1"       ;;
      *)         echo "Cannot extract '$1': unknown format" ;;
    esac
  else
    echo "'$1' is not a valid file."
  fi
}
