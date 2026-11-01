#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"

for tool in pandoc typst; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf '필수 도구를 찾을 수 없습니다: %s (설치: brew install pandoc typst)\n' "$tool" >&2
    exit 1
  fi
done

find "$repo_root" -type d -name .git -prune -o -type f -name '*.md' -print0 |
  while IFS= read -r -d '' markdown_file; do
    pdf_file="${markdown_file%.md} (Markdown).pdf"
    pandoc "$markdown_file" \
      --from=gfm \
      --pdf-engine=typst \
      -V mainfont="Apple SD Gothic Neo" \
      -V papersize=a4 \
      -o "$pdf_file"
    printf '생성: %s\n' "${pdf_file#"$repo_root"/}"
  done
