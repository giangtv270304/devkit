#!/usr/bin/env bash
# PreToolUse hook for Bash: exit 2 blocks the command, stderr is the reason shown to Claude.
# Only command-position words are inspected (start, or after ; && || | & ( ) `),
# so quoted text such as a commit message never triggers a rule.

if ! command -v jq >/dev/null 2>&1; then
  echo "bash-guard: jq not found, command check skipped" >&2
  exit 0
fi

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty')
[ -n "$cmd" ] || exit 0

block() {
  echo "bash-guard: $1" >&2
  exit 2
}

US=$'\x1f'
SEGS=()
cur=""
word=""
inword=0

flush_word() {
  if [ "$inword" = 1 ]; then cur="${cur}${word}${US}"; fi
  word=""
  inword=0
}
flush_seg() {
  flush_word
  if [ -n "$cur" ]; then SEGS+=("$cur"); fi
  cur=""
}

# Split into segments of unquoted words (quotes removed, bash 3.2 compatible).
q=""
ret=""
i=0
n=${#cmd}
while [ "$i" -lt "$n" ]; do
  c="${cmd:$i:1}"
  if [ "$q" = "'" ]; then
    if [ "$c" = "'" ]; then q=""; else word+="$c"; fi
  elif [ "$q" = '"' ]; then
    case "$c" in
      '"') q="" ;;
      '\') i=$((i + 1)); word+="${cmd:$i:1}" ;;
      '$')
        if [ "${cmd:$((i + 1)):1}" = "(" ]; then i=$((i + 1)); flush_seg; q=""; ret+="d"
        else word+="$c"; fi ;;
      *) word+="$c" ;;
    esac
  else
    case "$c" in
      "'" | '"') q="$c"; inword=1 ;;
      '\') i=$((i + 1)); word+="${cmd:$i:1}"; inword=1 ;;
      ' ' | $'\t') flush_word ;;
      ';' | '&' | '|' | $'\n' | '`') flush_seg ;;
      '(') flush_seg; ret+="p" ;;
      ')') flush_seg; [ "${ret: -1}" = d ] && q='"'; ret="${ret%?}" ;;
      *) word+="$c"; inword=1 ;;
    esac
  fi
  i=$((i + 1))
done
flush_seg

rm_target_ok() {
  local p="$1" rel part idx last tmpd
  local -a parts
  case "$p" in
    / | '~' | '~/' | '$HOME' | '${HOME}' | '$HOME/' | '${HOME}/' | .. | . | ./) return 1 ;;
    ../* | */.. | */../*) return 1 ;;
  esac
  tmpd="${TMPDIR%/}"
  case "$p" in
    /tmp/?* | /private/tmp/?* | '$TMPDIR'/?* | '${TMPDIR}'/?*) return 0 ;;
  esac
  if [ -n "$tmpd" ]; then
    case "$p" in "$tmpd"/?*) return 0 ;; esac
  fi
  case "$p" in
    /*)
      if [ -n "$cwd" ]; then
        case "$p" in "$cwd"/?*) rel="${p#"$cwd"/}" ;; *) return 1 ;; esac
      else
        return 1
      fi ;;
    '~'* | '$'*) return 1 ;;
    *) rel="${p#./}" ;;
  esac
  IFS=/ read -ra parts <<<"$rel"
  last=$((${#parts[@]} - 1))
  idx=0
  for part in "${parts[@]}"; do
    case "$part" in
      node_modules | dist | build | __pycache__) return 0 ;;
      worktrees) [ "$idx" -lt "$last" ] && return 0 ;;
    esac
    idx=$((idx + 1))
  done
  return 1
}

is_env_file() {
  local b="${1##*/}"
  b="${b#<}"
  case "$b" in
    .env.example | .env.sample | .env.template) return 1 ;;
    .env | .env.[A-Za-z0-9_-]*) return 0 ;;
  esac
  return 1
}

check_git() {
  local k=0 sub="" a
  while [ "$k" -lt "$#" ]; do
    k=$((k + 1))
    a="${!k}"
    case "$a" in
      -C | -c | --git-dir | --work-tree | --namespace) k=$((k + 1)) ;;
      -*) ;;
      *) sub="$a"; break ;;
    esac
  done
  [ -n "$sub" ] || return 0
  shift "$k"
  local force=0 dir=0
  case "$sub" in
    push)
      for a in "$@"; do
        case "$a" in
          --force | -f) force=1 ;;
          -[a-zA-Z]*) case "$a" in --*) ;; *f*) force=1 ;; esac ;;
        esac
      done
      [ "$force" = 1 ] && block "git push --force rewrites remote history. Use git push --force-with-lease." ;;
    reset)
      for a in "$@"; do
        [ "$a" = "--hard" ] && block "git reset --hard discards local work. Use git stash push -u -m <tag> or git reset --mixed."
      done ;;
    clean)
      for a in "$@"; do
        case "$a" in
          --force) force=1 ;;
          --*) ;;
          -*) case "$a" in *f*) force=1 ;; esac; case "$a" in *d*) dir=1 ;; esac ;;
        esac
      done
      [ "$force" = 1 ] && [ "$dir" = 1 ] && block "git clean -fd deletes untracked files for good. Use git clean -nd to preview, then name the paths." ;;
  esac
  return 0
}

check_rm() {
  local rec=0 frc=0 endopt=0 a
  local -a ops=()
  for a in "$@"; do
    if [ "$endopt" = 1 ]; then ops+=("$a")
    else
      case "$a" in
        --) endopt=1 ;;
        --recursive) rec=1 ;;
        --force) frc=1 ;;
        --*) ;;
        -?*) case "$a" in *[rR]*) rec=1 ;; esac; case "$a" in *f*) frc=1 ;; esac ;;
        *) ops+=("$a") ;;
      esac
    fi
  done
  [ "$rec" = 1 ] && [ "$frc" = 1 ] || return 0
  for a in ${ops[@]+"${ops[@]}"}; do
    rm_target_ok "$a" || block "rm -rf on '$a' is not allowed. Only /tmp, \$TMPDIR, node_modules, dist, build, __pycache__ or a worktree are; otherwise drop -f or name a safe path."
  done
  return 0
}

check_env_read() {
  local name="$1" a total n=0
  shift
  total=$#
  for a in "$@"; do
    n=$((n + 1))
    case "$a" in -*) continue ;; esac
    # cp: the last operand is the destination, only sources are reads
    [ "$name" = cp ] && [ "$n" = "$total" ] && continue
    is_env_file "$a" && block "$name on '$a' reads a real .env file. Read .env.example for variable names only."
  done
  return 0
}

for seg in ${SEGS[@]+"${SEGS[@]}"}; do
  IFS="$US" read -ra w <<<"$seg"
  k=0
  while [ "$k" -lt "${#w[@]}" ]; do
    t="${w[$k]}"
    case "$t" in
      [A-Za-z_]*=*) k=$((k + 1)) ;;
      sudo | env | command | builtin | exec | time | nohup | nice)
        k=$((k + 1))
        while [ "$k" -lt "${#w[@]}" ] && [[ "${w[$k]}" == -* ]]; do k=$((k + 1)); done ;;
      *) break ;;
    esac
  done
  [ "$k" -lt "${#w[@]}" ] || continue
  name="${w[$k]##*/}"
  [ -n "$name" ] || name="${w[$k]}"
  args=("${w[@]:$((k + 1))}")
  case "$name" in
    git) check_git ${args[@]+"${args[@]}"} ;;
    rm) check_rm ${args[@]+"${args[@]}"} ;;
    cat | head | tail | less | more | bat | source | . | grep | sed | awk | cp)
      check_env_read "$name" ${args[@]+"${args[@]}"} ;;
  esac
done
exit 0
