#!/usr/bin/env bash
# Usage: install.sh <dir> [<dir> ...]
# Each <dir> is a git repo, or a folder that holds git repos one level down.
# Hides AI tooling files from git (.git/info/exclude) and installs the pre-push guard. Safe to run again.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
[ "$#" -gt 0 ] || { echo "usage: $0 <repo or folder of repos> [...]" >&2; exit 2; }
begin="# >>> local-only AI files (devkit git-local) >>>"
end="# <<< local-only AI files <<<"

tmp=""
trap '[ -z "$tmp" ] || rm -f "$tmp"' EXIT

repos=()
for dir in "$@"; do
  dir="$(cd "$dir" && pwd)"
  if git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then repos+=("$dir"); continue; fi
  for sub in "$dir"/*/; do
    [ -d "$sub" ] || continue
    if git -C "$sub" rev-parse --git-dir >/dev/null 2>&1; then repos+=("${sub%/}"); fi
  done
done

[ "${#repos[@]}" -gt 0 ] || { echo "no git repo found in: $*" >&2; exit 1; }

for repo in "${repos[@]}"; do
  git_dir="$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir)"

  exclude="$git_dir/info/exclude"
  mkdir -p "$git_dir/info"
  touch "$exclude"
  tmp="$(mktemp)"
  awk -v b="$begin" -v e="$end" '$0==b{skip=1} !skip{print} $0==e{skip=0}' "$exclude" > "$tmp"
  { cat "$tmp"; echo "$begin"; cat "$here/ai-patterns.txt"; echo "$end"; } > "$exclude"
  rm -f "$tmp"
  tmp=""

  hooks_path="$(git -C "$repo" config --get core.hooksPath || true)"
  if [ -n "$hooks_path" ]; then
    echo "skip hook: $(basename "$repo") uses core.hooksPath=$hooks_path"
  else
    for name in pre-push commit-msg; do
      hook="$git_dir/hooks/$name"
      if [ -e "$hook" ] && ! grep -q 'git-local/install.sh' "$hook"; then
        echo "skip hook: $(basename "$repo") already has its own $name hook"
      else
        install -m 0755 "$here/$name" "$hook"
      fi
    done
  fi
  echo "ok: $(basename "$repo")"
done
echo "Hooks are copied, not linked: run this script again after you change a hook in git-local/."
