#!/usr/bin/env bash
# PostToolUse hook: format the file Claude just edited. Never blocks (always exits 0).
# Resolve symlinks so this works when run from ~/.claude/devkit/hooks.
src="${BASH_SOURCE[0]}"
while [ -L "$src" ]; do
  dir="$(cd "$(dirname "$src")" && pwd)"
  src="$(readlink "$src")"
  case "$src" in /*) ;; *) src="$dir/$src" ;; esac
done
# shellcheck source=lib/skip-generated.sh
. "$(cd "$(dirname "$src")" && pwd)/lib/skip-generated.sh"
input=$(cat)
file=$(printf '%s' "$input" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"\(.*\)"/\1/')
[ -n "$file" ] && [ -f "$file" ] || exit 0

is_generated "$file" && exit 0

case "$file" in
  *.go)
    if command -v gofumpt >/dev/null 2>&1; then gofumpt -w "$file"
    elif command -v gofmt >/dev/null 2>&1; then gofmt -w "$file"; fi ;;
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.json|*.css|*.md|*.yml|*.yaml)
    # Use the repo's own prettier only if that repo has one installed.
    dir=$(dirname "$file")
    while [ "$dir" != "/" ]; do
      if [ -x "$dir/node_modules/.bin/prettier" ]; then
        (cd "$dir" && ./node_modules/.bin/prettier --write --log-level=warn "$file") ; break
      fi
      [ -d "$dir/.git" ] && break
      dir=$(dirname "$dir")
    done ;;
esac
exit 0
