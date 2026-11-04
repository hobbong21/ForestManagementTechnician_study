#!/usr/bin/env bash
# 예상문제·모의고사·암기요약표 md → 08_PDF원문모음/05_예상문제, 06_모의고사, 07_암기요약표 PDF (git에 올림)
# 문제나 풀이를 고친 뒤: python3 tools/easy_explain.py apply && bash tools/build_question_pdfs.sh
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
conv() { pandoc "$1" --from=gfm --pdf-engine=typst -V mainfont="Apple SD Gothic Neo" \
  -V papersize=a4 -V margin.x=2cm -V margin.y=2cm -o "$2"; echo "생성: ${2#"$root"/}"; }
mkdir -p "$root/08_PDF원문모음/05_예상문제" "$root/08_PDF원문모음/06_모의고사" "$root/08_PDF원문모음/07_암기요약표"
for f in "$root"/04_예상문제/*.md; do conv "$f" "$root/08_PDF원문모음/05_예상문제/$(basename "${f%.md}").pdf"; done
for f in "$root"/05_모의고사/0*.md; do conv "$f" "$root/08_PDF원문모음/06_모의고사/$(basename "${f%.md}").pdf"; done
for f in "$root"/03_암기요약표/*.md; do conv "$f" "$root/08_PDF원문모음/07_암기요약표/$(basename "${f%.md}").pdf"; done
