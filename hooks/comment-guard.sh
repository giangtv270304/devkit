#!/usr/bin/env bash
set -u

# Resolve symlinks so this works when run from ~/.claude/devkit/hooks.
src="${BASH_SOURCE[0]}"
while [ -L "$src" ]; do
  dir="$(cd "$(dirname "$src")" && pwd)"
  src="$(readlink "$src")"
  case "$src" in /*) ;; *) src="$dir/$src" ;; esac
done
# shellcheck source=lib/skip-generated.sh
. "$(cd "$(dirname "$src")" && pwd)/lib/skip-generated.sh"

if ! command -v jq >/dev/null 2>&1; then
  echo "comment-guard: jq not found, comment check skipped" >&2
  exit 0
fi

input=$(cat)
tool=$(printf '%s' "$input" | jq -r '.tool_name // empty')
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')
[ -n "$file" ] || exit 0

is_generated "$file" && exit 0

case "${file##*.}" in
  go|ts|tsx|js|jsx|mjs|cjs) comment='^[[:space:]]*(//|/\*)' ;;
  sql) comment='^[[:space:]]*--' ;;
  *) exit 0 ;;
esac

directive='^[[:space:]]*(//go:|//nolint|// ?@|// ?\+build|//export |// ?eslint-|/\* ?eslint-|// ?@ts-|/// ?<reference|// ?prettier-ignore|//lint:|// ?#nosec|-- name: )'

case "$tool" in
  Edit)
    new=$(printf '%s' "$input" | jq -r '.tool_input.new_string // empty')
    old=$(printf '%s' "$input" | jq -r '.tool_input.old_string // empty') ;;
  MultiEdit)
    new=$(printf '%s' "$input" | jq -r '[.tool_input.edits[]?.new_string] | join("\n")')
    old=$(printf '%s' "$input" | jq -r '[.tool_input.edits[]?.old_string] | join("\n")') ;;
  Write)
    old=$(printf '%s' "$input" | jq -r '.tool_response.originalFile // empty')
    if [ -z "$old" ] && ! printf '%s' "$input" | jq -r '(.tool_response // "") | tostring' | grep -qi 'create'; then
      exit 0
    fi
    new=$(printf '%s' "$input" | jq -r '.tool_input.content // empty') ;;
  *) exit 0 ;;
esac
[ -n "$new" ] || exit 0

trim() { sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'; }
added=$(printf '%s\n' "$new" | trim | grep -E "$comment" | grep -Ev "$directive" | grep -vxF -f <(printf '%s\n' "$old" | trim) || true)
[ -n "$added" ] || exit 0

{
  printf 'comment-guard: new comment lines in %s\n' "$file"
  printf '%s\n' "$added" | head -n 8 | sed 's/^/  /'
  printf 'Delete them unless each passes the test in ~/.claude/rules/comments.md (external quirk or intentional oddity, required swag/godoc, nolint reason). Move the reason to the commit, PR or TASK.md, the intent to a name, the ops hint to the log message.\n'
} >&2
exit 2
