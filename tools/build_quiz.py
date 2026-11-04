"""04_예상문제/*.md 와 05_모의고사/00_2021년 공개문제 md 를 읽어 05_모의고사/모의고사.html 을 만든다.

문제 형식: '**번호.** 지문' 다음 줄들에 ①~④ 보기, 바로 아래 '> **정답:** ... > **해설:** ...'
문제를 고치면 이 스크립트를 다시 실행: python3 tools/build_quiz.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "04_예상문제"
OUT = ROOT / "05_모의고사" / "모의고사.html"
PUBLIC_SRC = ROOT / "05_모의고사" / "00_2021년_필기시험_공개문제_38제.md"
TEMPLATE = Path(__file__).resolve().parent / "quiz_template.html"

SUBJECTS = [
    ("01", "조림", "필수"),
    ("02", "산림보호", "필수"),
    ("03", "산림경영", "필수"),
    ("04", "산림관계법규", "필수"),
    ("05", "산림토목", "선택"),
    ("06", "임산가공", "선택"),
]
MARKS = "①②③④"


def explain_lines(quote):
    """'>' 블록에서 정답·출제 근거를 뺀 해설 줄을 모아 CBT 표시용 텍스트로 만든다('- 항목'은 '· 항목')."""
    out = []
    for line in quote:
        line = line.lstrip(">").strip()
        if not line or line.startswith("**정답:**") or line.startswith("**출제 근거:**"):
            continue
        line = re.sub(r"^-\s+", "· ", line.replace("**해설:**", "").strip())
        if line:
            out.append(line)
    return re.sub(r"\*\*", "", "\n".join(out))


def parse(path, subject):
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"^(?=\*\*\d+\.\*\* )", text, flags=re.M)
    questions = []
    for block in blocks[1:]:
        m = re.match(r"\*\*(\d+)\.\*\*\s*(.*)", block, re.S)
        if not m:
            continue
        num = int(m.group(1))
        body = re.split(r"^(?:---|## )", m.group(2), flags=re.M)[0].strip()

        m_ans = re.search(r">\s*\*\*정답:\*\*\s*([①②③④])", body)
        m_ref = re.search(r">\s*\*\*출제 근거:\*\*\s*(.*?)(?:\n|$)", body)

        if not m_ans:
            raise SystemExit(f"{path.name} {num}번: 정답 없음")

        ans = MARKS.index(m_ans.group(1))
        expl = explain_lines(l for l in body.splitlines() if l.startswith(">"))
        ref = m_ref.group(1).strip() if m_ref else ""

        q_content = re.split(r"\n\s*>", body)[0].strip()
        parts = re.split(r"([①②③④])", q_content)
        stem = parts[0].strip()
        options = [p.strip() for p in parts[2::2]]

        if len(options) != 4:
            raise SystemExit(f"{path.name} {num}번: 보기 {len(options)}개")

        part = 1 if num <= 20 else 2 if num <= 40 else 3 if num <= 50 else 4 if num <= 100 else 5
        questions.append({
            "id": f"{subject}-{num}",
            "subject": subject,
            "num": num,
            "part": part,
            "stem": stem,
            "options": options,
            "answer": ans,
            "explain": expl,
            "ref": ref,
        })
    return questions


PUB_MARKS = "가나다라"
PUB_OPT = re.compile(r"(?:^|\s{2,})(?:([가나다라마])\.|([①②③④]))\s*(.*?)(?=\s{2,}(?:[가나다라마]\.|[①②③④])|$)")


def plain(text):
    """공개문제 지문의 md 표·강조를 CBT용 일반 텍스트로 바꾼다."""
    lines = []
    for line in text.splitlines():
        if re.match(r"^\|[-| ]+\|$", line):
            continue
        if line.startswith("|"):
            line = " | ".join(c.strip() for c in line.strip("|").split("|"))
        lines.append(line)
    return re.sub(r"\*\*", "", "\n".join(lines)).strip()


def parse_public(path):
    """'## 제N과목: 이름' 아래 '**[문제 NN]**' 블록. 보기는 가~라(또는 ①~④), 공통 지문은 해당 문항들 앞에 붙인다."""
    data = []
    for sec in re.split(r"^## (?=제\d과목)", path.read_text(encoding="utf-8"), flags=re.M)[1:]:
        name = re.match(r"제\d과목:\s*(\S+)", sec).group(1)
        shared = {}
        questions = []
        for block in re.split(r"^(?=\*\*\[문제 )", sec, flags=re.M)[1:]:
            block = re.split(r"^---", block, flags=re.M)[0].strip()
            m = re.match(r"\*\*\[문제 (\d+)(?:~(\d+))?([^\]]*)\]\*\*\s*(.*)", block, re.S)
            lo, hi, rest = int(m.group(1)), m.group(2), m.group(4)
            if hi:
                for n in range(lo, int(hi) + 1):
                    shared[n] = plain(rest)
                continue
            q_part, _, a_part = rest.partition("\n>")
            stem, options, marks = [], [], []
            for line in q_part.strip().splitlines():
                if re.match(r"^(?:[가나다라마]\.|[①②③④])", line.strip()):
                    for g1, g2, txt in PUB_OPT.findall(line.strip()):
                        marks.append("①②③④"[len(options)] if g2 else PUB_MARKS[len(options)] + ".")
                        options.append(txt.strip())
                else:
                    stem.append(line)
            if len(options) != 4:
                raise SystemExit(f"공개문제 {name} {lo}번: 보기 {len(options)}개")
            quote = [l.lstrip("> ").rstrip() for l in ("> " + a_part).splitlines() if l.startswith(">")]
            ans_line = next(l for l in quote if l.startswith("**정답:**"))
            picks = re.findall(r"[가나다라①②③④]", ans_line.replace("**정답:**", ""))
            idx = [("가나다라".index(c) if c in "가나다라" else "①②③④".index(c)) for c in picks]
            ref = next((l.replace("**출제 근거:**", "").strip() for l in quote if l.startswith("**출제 근거:**")), "")
            expl = explain_lines(quote)
            note = "⚠️ 확인 필요\n" if "⚠️" in ans_line else ""
            body = plain("\n".join(stem))
            if lo in shared:
                body = f"[공통 지문] {shared[lo]}\n\n{body}"
            questions.append({
                "id": f"공개-{name}-{lo}",
                "subject": name,
                "num": lo,
                "part": 0,
                "stem": body,
                "options": options,
                "marks": marks,
                "answer": idx[0],
                "accept": sorted(set(idx)),
                "explain": note + expl,
                "ref": ref,
            })
        data.append({"name": name, "questions": questions})
    return data


def main():
    data = []
    for code, name, kind in SUBJECTS:
        path = next(SRC.glob(f"{code}_*.md"))
        data.append({"code": code, "name": name, "kind": kind, "questions": parse(path, name)})
    public = parse_public(PUBLIC_SRC)
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        "/*__DATA__*/null", json.dumps(data, ensure_ascii=False)).replace(
        "/*__PUBLIC__*/null", json.dumps(public, ensure_ascii=False))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    total = sum(len(s["questions"]) for s in data)
    n_pub = sum(len(s["questions"]) for s in public)
    print(f"{OUT.relative_to(ROOT)}: 예상 {total}문항 + 2021 공개문제 {n_pub}문항 빌드 완료")


if __name__ == "__main__":
    main()
