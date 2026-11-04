"""문제 해설에 '쉬운 풀이'·'용어 풀이'를 붙인다 (고등학생 눈높이 보강).

데이터: tools/easy_explain/<키>.json  — {"번호": {"e": "쉬운 풀이", "t": "용어1: 뜻 / 용어2: 뜻"}}
  키: 04_예상문제 파일은 '01'~'06', 공개문제는 'pub', 국가직 9급 기출은 '9급-2026-조림' 형식

사용:
  python3 tools/easy_explain.py dump <키> [시작] [끝]   # 풀이 작성용으로 문항 요약 출력
  python3 tools/easy_explain.py apply                    # json 내용을 md에 반영 (여러 번 실행해도 같은 결과)

반영 위치: 각 문항 정답 블록(>) 안, '해설' 다음·'출제 근거' 앞
  > **쉬운 풀이:** ...
  > **용어 풀이:**
  > - 용어: 뜻
05_모의고사/01·02 실전모의고사는 '(원문 #N)' 번호로 04_예상문제의 같은 문항 풀이를 그대로 가져온다.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(__file__).resolve().parent / "easy_explain"
Q4 = ROOT / "04_예상문제"
M5 = ROOT / "05_모의고사"
PUB = M5 / "00_2021년_필기시험_공개문제_38제.md"
GM = next(M5.glob("03_국가직9급_*.md"))
MOCKS = sorted(M5.glob("0[12]_전과목_실전모의고사_100제.md"))
SUBJ_OF_MOCK = {"조림": "01", "산림보호": "02", "임업경영": "03", "산림경영": "03", "산림관계법규": "04", "산림토목": "05", "임산가공": "06"}


def load(key):
    p = DATA / f"{key}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def blocks(text, head):
    """(시작, 끝, 번호, 블록문자열) — 문항 머리 정규식 head 의 group(1)이 번호"""
    ms = list(re.finditer(head, text, re.M))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        seg = text[m.start():end]
        cut = re.search(r"^(---|## )", seg, re.M)
        if cut:
            end = m.start() + cut.start()
        yield m.start(), end, m.group(1), text[m.start():end], m


def summarize(block):
    lines = [l for l in block.splitlines() if l.strip()]
    q = " ".join(l for l in lines if not l.startswith(">"))
    a = " ".join(l.lstrip("> ").strip() for l in lines if l.startswith(">")
                 and "쉬운 풀이" not in l and "용어 풀이" not in l)
    q = re.sub(r"\s+", " ", q)[:420]
    a = re.sub(r"\s+", " ", a)[:420]
    return f"{q}\n   ⇒ {a}"


def strip_easy(block):
    out, skip = [], False
    for l in block.split("\n"):
        s = l.lstrip(">").strip()
        if s.startswith("**쉬운 풀이:**") or s.startswith("**용어 풀이:**"):
            skip = True
            if out and out[-1].strip() == ">":
                out.pop()
            continue
        if skip and (s.startswith("- ") or (s and not s.startswith("**"))):
            continue
        if skip and s == "":
            continue
        skip = False
        out.append(l)
    return "\n".join(out)


def inject(block, item):
    block = strip_easy(block)
    if not item:
        return block
    add = [">", f"> **쉬운 풀이:** {item['e'].strip()}"]
    terms = [t.strip() for t in re.split(r"\s*/\s*(?=[^/]+:)", item.get("t", "")) if t.strip()]
    if terms:
        add += [">", "> **용어 풀이:**"] + [f"> - {t}" for t in terms]
    lines = block.rstrip("\n").split("\n")
    # 출제 근거·중요도 앞, 없으면 정답 블록 끝
    idx = next((i for i, l in enumerate(lines) if re.match(r">\s*\*\*(출제 근거|중요도):\*\*", l)), None)
    if idx is None:
        idx = max(i for i, l in enumerate(lines) if l.startswith(">")) + 1
        while lines[idx - 1].strip() == ">":
            idx -= 1
            del lines[idx]
        lines[idx:idx] = add
    else:
        while lines[idx - 1].strip() == ">":
            idx -= 1
            del lines[idx]
        lines[idx:idx] = add + [">"]
    tail = "\n" if block.endswith("\n") else ""
    return "\n".join(lines) + tail + ("\n" if block.endswith("\n\n") else "")


def rewrite(path, head, keyfn):
    text = path.read_text(encoding="utf-8")
    out, pos, n = [], 0, 0
    for s, e, num, blk, m in blocks(text, head):
        item = keyfn(num, m, text[:s])
        out += [text[pos:s], inject(blk, item)]
        pos = e
        n += bool(item)
    out.append(text[pos:])
    new = "".join(out)
    if new != text:
        path.write_text(new, encoding="utf-8")
    return n


def q4_files():
    return {p.name[:2]: p for p in sorted(Q4.glob("0*_*.md"))}


HEAD4 = r"^\*\*(\d+)\.\*\* "
HEADPUB = r"^\*\*\[문제 (\d+)\]"
HEADMOCK = r"^\*\*\[(?:선택)?문제 \d+\] \(원문 #(\d+)\)\*\*"


def gm_key(prefix_text):
    secs = re.findall(r"^## (\d{4}) (조림|임업경영)$", prefix_text, re.M)
    return f"9급-{secs[-1][0]}-{secs[-1][1]}" if secs else None


def mock_subject(prefix_text):
    secs = re.findall(r"^## .*?(조림|산림보호|임업경영|산림경영|산림관계법규|산림토목|임산가공)", prefix_text, re.M)
    return SUBJ_OF_MOCK.get(secs[-1]) if secs else None


def pub_subject(prefix_text):
    secs = re.findall(r"^## 제\d과목:\s*(\S+)", prefix_text, re.M)
    return secs[-1] if secs else None


def apply():
    total = 0
    cache = {}
    get = lambda k: cache.setdefault(k, load(k))
    for code, p in q4_files().items():
        total += rewrite(p, HEAD4, lambda num, m, pre, c=code: get(c).get(num))
    total += rewrite(PUB, HEADPUB, lambda num, m, pre: get("pub").get(f"{pub_subject(pre)}-{num}"))
    total += rewrite(GM, HEAD4, lambda num, m, pre: get(gm_key(pre) or "-").get(num))
    for mp in MOCKS:
        total += rewrite(mp, HEADMOCK, lambda num, m, pre: get(mock_subject(pre) or "-").get(num))
    print(f"쉬운 풀이 반영: {total}문항")


def dump(key, lo=1, hi=999):
    if key in q4_files():
        path, head, filt = q4_files()[key], HEAD4, lambda pre: True
    elif key == "pub":
        path, head, filt = PUB, HEADPUB, lambda pre: True
    else:
        path, head, filt = GM, HEAD4, lambda pre: gm_key(pre) == key
    text = path.read_text(encoding="utf-8")
    for s, e, num, blk, m in blocks(text, head):
        pre = text[:s]
        if not filt(pre) or not (lo <= int(num) <= hi):
            continue
        tag = f"{pub_subject(pre)}-{num}" if key == "pub" else num
        print(f"[{tag}] {summarize(blk)}")


if __name__ == "__main__":
    if sys.argv[1] == "apply":
        apply()
    else:
        dump(sys.argv[2], *(int(x) for x in sys.argv[3:5]))
