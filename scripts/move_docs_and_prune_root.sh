#!/usr/bin/env bash
set -euo pipefail

# move_docs_and_prune_root.sh
# Safe utility to collect top-level documentation files into /docs and optionally archive/move
# certain top-level directories (like ai-dev-tasks, tasks) into /docs.
# Default mode: dry-run (shows planned moves). Use --apply to perform the moves.
# Usage:
#   ./scripts/move_docs_and_prune_root.sh        # dry-run
#   ./scripts/move_docs_and_prune_root.sh --apply  # perform moves (uses git mv when possible)

DRY_RUN=1
ARCHIVE_DIR="docs"
APPLY_FLAG="--apply"

if [[ ${1-} == "${APPLY_FLAG}" ]]; then
  DRY_RUN=0
fi

# Top-level items to always keep in root
KEEP=(
  "app.py"
  "Dockerfile"
  "docker-compose.yml"
  "requirements.txt"
  "README.md"
  "deploy.yaml"
  ".gitignore"
  ".github"
  "pages"
  "utils"
  "models"
  "config"
  "scripts"
)

# Top-level directories we may want to move into docs when present
DIR_CANDIDATES=(
  "ai-dev-tasks"
  "tasks"
)

# Ensure running from repo root (where this script lives at scripts/)
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p "$ARCHIVE_DIR"

is_keep() {
  local name="$1"
  for k in "${KEEP[@]}"; do
    if [[ "$name" == "$k" ]]; then
      return 0
    fi
  done
  return 1
}

is_dir_candidate() {
  local name="$1"
  for d in "${DIR_CANDIDATES[@]}"; do
    if [[ "$name" == "$d" ]]; then
      return 0
    fi
  done
  return 1
}

candidates=()

# Collect top-level items
while IFS= read -r -d $'\0' item; do
  name="${item#./}"
  # skip dotfiles and script directory
  if [[ "$name" == ".git" || "$name" == "scripts" ]]; then
    continue
  fi
  if is_keep "$name"; then
    continue
  fi
  # files with doc-like extensions
  if [[ -f "$item" ]]; then
    ext="${name##*.}"
    if [[ "$ext" == "md" || "$ext" == "pdf" || "$ext" == "txt" || "$ext" == "rst" || "$ext" == "mdx" ]]; then
      # explicitly preserve README.md in root
      if [[ "$name" == "README.md" ]]; then
        continue
      fi
      candidates+=("$name")
    fi
  elif [[ -d "$item" ]]; then
    # consider specific dirs for archiving
    if is_dir_candidate "$name"; then
      candidates+=("$name")
    fi
  fi
done < <(find . -maxdepth 1 -mindepth 1 -print0)

if [[ ${#candidates[@]} -eq 0 ]]; then
  echo "No candidate docs or directories found to move into '$ARCHIVE_DIR'."
  exit 0
fi

echo "Found ${#candidates[@]} candidate(s) to move into '$ARCHIVE_DIR':"
for c in "${candidates[@]}"; do
  echo "  - $c"
done

if [[ $DRY_RUN -eq 1 ]]; then
  echo
  echo "DRY-RUN mode (no changes). To perform moves, re-run with --apply."
  echo
  echo "Planned operations (example):"
  for c in "${candidates[@]}"; do
    echo "  mv $c $ARCHIVE_DIR/"
  done
  echo
  echo "Tip: review output and then run: ./scripts/move_docs_and_prune_root.sh --apply"
  exit 0
fi

# Apply moves. Prefer git mv when inside a git repo and file is tracked.
is_git_repo=0
if git rev-parse --git-dir > /dev/null 2>&1; then
  is_git_repo=1
fi

for c in "${candidates[@]}"; do
  target="$ARCHIVE_DIR/$c"
  # ensure target directory exists
  mkdir -p "$(dirname "$target")"
  if [[ $is_git_repo -eq 1 ]]; then
    # if tracked file/dir -> git mv, else fallback to mv
    if git ls-files --error-unmatch "$c" > /dev/null 2>&1; then
      echo "git mv '$c' '$target'"
      git mv -- "$c" "$target"
    else
      echo "mv '$c' '$target' (not tracked by git)"
      mv -- "$c" "$target"
      # add to git
      git add -- "$target"
    fi
  else
    echo "mv '$c' '$target'"
    mv -- "$c" "$target"
  fi
done

# After moves, suggest a commit message
if [[ $is_git_repo -eq 1 ]]; then
  echo
  echo "All items moved. Next steps: review changes and run:"
  echo "  git status --porcelain"
  echo "  git add -A"
  echo "  git commit -m \"chore(docs): move top-level documentation into /docs\""
  echo "  git push"
else
  echo "Moves performed outside git. If you want versioning, initialize git or move under git control."
fi

exit 0
