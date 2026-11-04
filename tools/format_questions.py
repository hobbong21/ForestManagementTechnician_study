"""문제 md 의 가독성 정리: 보기는 한 줄에 하나씩, 정답·해설·근거는 문단을 나누고 긴 해설은 항목별 줄로 나눈다.

대상: 04_예상문제/*.md, 05_모의고사/0*.md (문항 머리 '**N.**' 또는 '**[문제 ...]**')
여러 번 실행해도 결과가 같다. 실행: python3 tools/format_questions.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = sorted((ROOT / "04_예상문제").glob("*.md")) + sorted((ROOT / "05_모의고사").glob("0*.md"))

HEAD = re.compile(r"^\*\*(?:\d+\.|\[문제 [^\]]+\][^*]*)\*\*")
NUM_OPT = re.compile(r"(?:^|(?<=\s\s))(?=[①②③④])")
KOR_OPT = re.compile(r"(?:^|(?<=\s\s))(?=[가나다라마]\.\s)")
FIELD = re.compile(r"^\*\*(정답|해설|쉬운 풀이|용어 풀이|출제 근거|중요도):\*\*\s*(.*)$")


def split_options(line):
    s = line.strip()
    pat = NUM_OPT if s[0] in "①②③④" else KOR_OPT
    return [p.strip() for p in pat.split(s) if p.strip()]


def is_option(line):
    return bool(re.match(r"^(?:[①②③④]|[가나다라마]\.\s)", line.strip()))


def split_explain(text):
    """' · ', 한글 사이의 ' / ', 문장 끝('다. ')에서 나눈다. 수식(숫자·괄호 옆의 /)은 나누지 않는다."""
    parts = re.split(r"(?<=[가-힣)\]])\s+·\s+(?=[가-힣(\[])|(?<=[^\d()\s])\s/\s(?=[^\d()\s])|(?<=다\.)\s+(?=\S)", text)
    return [p.strip() for p in parts if p.strip()]


def format_question(lines):
    q_lines, a_lines = [], []
    for line in lines:
        (a_lines if line.startswith(">") or a_lines else q_lines).append(line)

    stem, options = [], []
    for line in q_lines:
        if not line.strip():
            continue
        if is_option(line) and stem:
            options.extend(split_options(line))
        else:
            stem.append(line.rstrip())

    out = []
    for i, line in enumerate(stem):
        # 표는 줄을 붙여 두고, 나머지 지문 줄은 문단으로 나눈다
        if i and not (line.startswith("|") and stem[i - 1].startswith("|")):
            out.append("")
        out.append(line)
    out.append("")
    for i, opt in enumerate(options):
        if i:
            out.append("")
        out.append(opt)

    fields, extra, cur = {}, [], None
    for raw in a_lines:
        line = raw.lstrip(">").strip()
        if not line:
            continue
        m = FIELD.match(line)
        if m:
            cur = m.group(1)
            fields.setdefault(cur, [])
            if m.group(2):
                fields[cur].append(m.group(2).strip())
        elif cur in ("쉬운 풀이", "용어 풀이"):
            fields[cur].append(line)
        elif cur == "해설" or cur is None:
            fields.setdefault("해설", []).append(re.sub(r"^[-·]\s*", "", line))
        else:
            extra.append(line)

    if fields or extra:
        out.append("")
        block = []
        if "정답" in fields:
            block.append(f"**정답:** {' '.join(fields['정답'])}")
        if fields.get("해설"):
            items = [p for chunk in fields["해설"] for p in split_explain(chunk)]
            block.append("")
            if len(items) == 1:
                block.append(f"**해설:** {items[0]}")
            else:
                block.append("**해설:**")
                block.extend(f"- {p}" for p in items)
        for e in extra:
            block += ["", e]
        if fields.get("쉬운 풀이"):
            block += ["", f"**쉬운 풀이:** {' '.join(fields['쉬운 풀이'])}"]
        if fields.get("용어 풀이"):
            block += ["", "**용어 풀이:**"] + ["- " + re.sub(r"^[-·]\s*", "", x) for x in fields["용어 풀이"]]
        if fields.get("출제 근거"):
            block += ["", f"**출제 근거:** {' '.join(fields['출제 근거'])}"]
        if fields.get("중요도"):
            block += ["", f"**중요도:** {' '.join(fields['중요도'])}"]
        out.extend(f"> {b}" if b else ">" for b in block)
    return out


def format_text(text):
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        if HEAD.match(lines[i]):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("---") and not HEAD.match(lines[j]) \
                    and not lines[j].startswith("## "):
                j += 1
            block = lines[i:j]
            while block and not block[-1].strip():
                block.pop()
            out.extend(format_question(block))
            out.append("")
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def main():
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        new = format_text(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"정리: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
