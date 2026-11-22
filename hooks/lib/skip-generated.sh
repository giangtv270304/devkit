#!/usr/bin/env bash
# Shared by the edit hooks. is_generated <file>: true for files nobody edits by hand.
is_generated() {
  case "$1" in
    */apispec/*|*/docs/swagger.*|*/docs/docs.go|*/node_modules/*|*/dist/*|*/mocks/*|*.generated.*|*_gen.go|*.pb.go|*.gen.ts|*.d.ts) return 0 ;;
  esac
  return 1
}
