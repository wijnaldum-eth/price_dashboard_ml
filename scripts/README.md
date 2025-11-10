move_docs_and_prune_root.sh

Purpose
- Collect top-level documentation files (e.g., .md, .pdf, .txt) and archive them under `/docs`.
- Optionally archive specific top-level directories (like `ai-dev-tasks` and `tasks`) into `/docs`.

Safety
- Default behavior is a dry-run: it prints the planned moves and exits.
- Use `--apply` to perform moves. When run in a git repository the script will prefer `git mv` for tracked files and `git add` for untracked moved files.

Usage
- Dry-run (recommended first):

```bash
./scripts/move_docs_and_prune_root.sh
```

- Apply moves:

```bash
./scripts/move_docs_and_prune_root.sh --apply
```

Notes
- The script keeps a small set of important root files/dirs in place (see the KEEP array in the script). `README.md` is intentionally kept in the repository root.
- You can edit `DIR_CANDIDATES` in the script to add/remove directories that should be archived into `/docs`.
- After running with `--apply`, review `git status`, commit the changes, and push.

Example commit message:

  chore(docs): move top-level documentation into /docs

If you'd like, I can update the list of `KEEP` entries based on a quick scan of this repository or run a dry-run here and show the planned moves.