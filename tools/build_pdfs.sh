#!/usr/bin/env bash
# (선택) md 문서를 인쇄용 PDF로 변환합니다. 결과는 08_PDF원문모음/00_MD변환본/ 에 저장되며 git에는 올리지 않습니다(.gitignore).
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
out_root="$repo_root/08_PDF원문모음/00_MD변환본"

for tool in pandoc typst; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf '필수 도구를 찾을 수 없습니다: %s (설치: brew install pandoc typst)\n' "$tool" >&2
    exit 1
  fi
done

find "$repo_root" -type d \( -name .git -o -name 08_PDF원문모음 -o -name tools \) -prune -o -type f -name '*.md' -print0 |
  while IFS= read -r -d '' markdown_file; do
    rel="${markdown_file#"$repo_root"/}"
    pdf_file="$out_root/${rel%.md}.pdf"
    mkdir -p "$(dirname "$pdf_file")"
    pandoc "$markdown_file" \
      --from=gfm \
      --pdf-engine=typst \
      -V mainfont="Apple SD Gothic Neo" \
      -V papersize=a4 \
      -o "$pdf_file"
    printf '생성: %s\n' "${pdf_file#"$repo_root"/}"
  done
