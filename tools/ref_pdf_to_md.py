"""08_PDF원문모음/03_참조자료/**/*.pdf → 01_공식자료/03_참조자료/**/*.md

법령·행정규칙·별표 PDF(국가법령정보센터)의 텍스트를 추출해 읽기 좋은 Markdown으로 만든다.
- 텍스트 추출: macOS PDFKit (tools/pdftext.swift를 컴파일해 사용)
- 장·절·조문은 제목으로, 항(①)·호(1.)·목(가.)은 줄을 나눠 정리
- PDF 줄바꿈으로 끊긴 문장을 다시 이어 붙임
- 별표의 표는 텍스트 추출 한계로 칸이 섞일 수 있어, 원본 PDF 링크를 문서 머리에 둔다

사용: python3 tools/ref_pdf_to_md.py   (기존 md는 덮어씀, .hwpx 요약 md는 건드리지 않음)
"""
import html
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "08_PDF원문모음" / "03_참조자료"
DST = ROOT / "01_공식자료" / "03_참조자료"
SWIFT = Path(__file__).resolve().parent / "pdftext.swift"

nfc = lambda s: unicodedata.normalize("NFC", s)


def extractor():
    exe = Path(tempfile.gettempdir()) / "pdftext_bin"
    if not exe.exists() or exe.stat().st_mtime < SWIFT.stat().st_mtime:
        subprocess.run(["swiftc", "-O", str(SWIFT), "-o", str(exe)], check=True)
    return exe


def pdf_text(exe, pdf):
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        out = Path(f.name)
    subprocess.run([str(exe), str(pdf), str(out)], check=True, capture_output=True)
    t = out.read_text(encoding="utf-8")
    out.unlink()
    return nfc(t)


NOISE = [
    r"^법제처\s*\d+\s*국가법령정보센터$", r"^법령, 판례 등 모든 법령정보를 한 번에 검색 OK !$",
    r"^법제처 국가법령정보센터$", r"^www\.law\.go\.kr$", r"^\d{4}\.\d{2}\.\d{2}$", r"^￼$",
    r"^•\s*(판례|연혁|위임행정규칙|규제|한눈보기|위임법령|조문체계도)?$", r"^(일부개정|전부개정|제정|타법개정)$",
    r"^제\d+호$", r"^출처: 국가법령정보센터", r"^\d{4}\. \d{1,2}\. ?\d{0,2}$", r"^\d{1,2}$",
]
NOISE = [re.compile(p) for p in NOISE]

# 새 줄로 시작해야 하는 구조 표시
START = re.compile(
    r"^(제\d+(의\d+)?(장|절|관|조)|[①-⑳]|\([가-하]\)\s|\d+(의\d+)?\.\s|[가-하]\.\s|\d+\)\s|[가-하]\)\s|\(\d+\)|부\s*칙|"
    r"\[별표|\[부속서|■|※|<|\[시행|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\.|○|◦|-\s|·\s|\|)"
)
UNIT = re.compile(r"^(호|조|항|목|세|개|년|월|일|미터|센티|킬로|퍼센트|제곱|만원|원|명|인|회|배|도|시간|분|본|그루|헥타르|ha|%)")


_W = {}
def pref_whole(toks):
    key = id(toks)
    if key not in _W:
        _W.clear(); _W[key] = set(toks)
    return _W[key]


def join_lines(lines):
    toks = re.findall(r"[가-힣]{2,}", " ".join(lines))
    pref = {w[:k] for w in toks for k in range(2, len(w) + 1)}
    out = []
    for ln in lines:
        if out and re.search(r"(\d{4}\.|\d{1,2}\.)$", out[-1]) and re.match(r"^\d{1,2}\. ?\d", ln):
            out[-1] += " " + ln  # 날짜가 줄바꿈으로 끊긴 경우 (2019.\n7. 2.)
            continue
        if not out or START.match(ln) or not out[-1]:
            out.append(ln)
            continue
        prev = out[-1]
        if prev.endswith(("다.", "다)", ":", "음", "함", "것")) and len(prev) < 40:
            out.append(ln)
            continue
        sep = "" if re.search(r"\d$", prev) and UNIT.match(ln) else " "
        a = re.search(r"([가-힣]+)$", prev); b = re.match(r"^([가-힣]+)", ln)
        if a and b and len(a.group(1)) <= 4 and (a.group(1) + b.group(1)[:2]) in pref and a.group(1) not in pref_whole(toks):
            sep = ""
        out[-1] = prev + sep + ln
    return out


def to_md(text, title="", annex=False):
    text = html.unescape(text).replace("ᆞ", "·")
    text = re.sub(r"\s(\([가-하]\)|\(\d+\))\s", r"\n\1 ", text)
    raw = [l.strip() for l in text.replace("\f", "\n").splitlines()]
    raw = [l for l in raw if l != title]
    raw = [l for l in raw if l and not any(p.match(l) for p in NOISE) and "img id=" not in l]
    lines = join_lines(raw)
    has_article = any(re.match(r"^제\d+조", l) for l in lines)
    md = []
    for ln in lines:
        m = re.match(r"^(제\d+(?:의\d+)?(?:장|절|관))\s*(.*)$", ln)
        if m and len(ln) < 50:
            md += ["", f"## {m.group(1)} {m.group(2)}".rstrip(), ""]
            continue
        m = re.match(r"^(제\d+조(?:의\d+)?(?:\([^)]*\))?)\s*(.*)$", ln)
        if m and not annex:
            md += ["", f"### {m.group(1)}", ""]
            if m.group(2):
                md.append(m.group(2))
            continue
        if re.match(r"^부\s*칙", ln) and len(ln) < 40:
            md += ["", f"## {ln}", ""]
            continue
        if (re.match(r"^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\.", ln) or (not has_article and re.match(r"^\d+\.\s", ln))) and len(ln) < 30:
            md += ["", f"#### {ln}", ""]
            continue
        if re.match(r"^[①-⑳]", ln):
            md += ["", ln]
            continue
        if re.match(r"^(\d+(의\d+)?\.|[가-하]\.|\d+\)|[가-하]\))\s", ln):
            ind = "  " if re.match(r"^([가-하]\.|\d+\))", ln) else ""
            ind = "    " if re.match(r"^[가-하]\)", ln) else ind
            md.append(f"{ind}- {ln}")
            continue
        md += ["", ln]
    s = "\n".join(md)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s


# 시험에 자주 나오는 표는 손으로 정리한 표를 덧붙인다 (파일명 앞부분 → md)
SUPPLEMENT = {
    "[별표 3] 기준벌기령": """## ✍️ 정리 표: 기준벌기령 (원본 PDF 대조)

| 수종 | 국유림 | 공·사유림 (기업경영림) |
|---|---|---|
| 소나무 (춘양목보호림단지) | 60년 (100년) | 40년(30년) (100년) |
| 잣나무 | 60년 | 50년(40년) |
| 리기다소나무 | 30년 | 25년(20년) |
| 낙엽송 | 50년 | 30년(20년) |
| 삼나무 | 50년 | 30년(30년) |
| 편백 | 60년 | 40년(30년) |
| 기타 침엽수 | 60년 | 40년(30년) |
| 참나무류 | 60년 | 25년(20년) |
| 포플러류 | 3년 | 3년 |
| 기타 활엽수 | 60년 | 40년(20년) |

- 특수용도기준벌기령(펄프·갱목·표고·영지·천마·목공예·숯·목초액·섬유판·산림바이오매스에너지): 일반기준벌기령 중 **기업경영림** 기준 적용. 단, **소나무는 적용하지 않음**
- 불량림 수종갱신·피해목·지장목 벌채, **임지생산능력 Ⅰ~Ⅲ급지의 리기다소나무 벌채**는 기준벌기령을 적용하지 않음
- 모두베기 1개 벌채구역 최대 **30만㎡** · 5만㎡ 이상(임업후계자·독림가는 10만㎡ 이상)이면 **20% 이상** 군상·수림대로 존치

---

""",
}


def meta(stem):
    # 예: 산림보호법 시행령(대통령령)(제36066호)(20260201)
    m = re.match(r"^(.*)\(([^()]*)\)\((제[^()]*호)\)\((\d{8})\)$", stem)
    if m:
        name, kind, no, d = m.groups()
        return name, f"{kind} {no} · 시행 {d[:4]}.{int(d[4:6])}.{int(d[6:])}."
    m = re.match(r"^(\[(?:별표|부속서)[^\]]*\])\s*(.*)\(([^()]*)\)$", stem)
    if m:
        tag, title, law = m.groups()
        return f"{tag} {title}", f"「{law}」 별표·부속서"
    return stem, ""


def main():
    exe = extractor()
    n = 0
    for pdf in sorted(SRC.rglob("*.pdf")):
        rel = pdf.relative_to(SRC)
        dst = DST / rel.with_suffix(".md")
        dst.parent.mkdir(parents=True, exist_ok=True)
        title, info = meta(nfc(pdf.stem))
        body = to_md(pdf_text(exe, pdf), title.split("] ")[-1] if title.startswith("[") else title, annex=title.startswith("["))
        up = "../" * (len(rel.parts) + 1)
        link = f"{up}08_PDF원문모음/03_참조자료/{rel.as_posix()}"
        head = [f"# {title}", "", f"> {info}" if info else "> 참조자료 원문",
                f"> 원본 PDF: [{nfc(pdf.name)}](<{link}>) · 국가법령정보센터(law.go.kr) 원문을 2026.11.3 내려받음",
                "> ⚠️ PDF에서 텍스트를 추출해 정리했습니다. 표는 칸이 섞일 수 있으니 수치는 원본 PDF로 확인하세요.", "", "---", ""]
        sup = next((v for k, v in SUPPLEMENT.items() if nfc(pdf.name).startswith(k)), "")
        dst.write_text("\n".join(head) + sup + "## 원문\n\n" + body + "\n", encoding="utf-8")
        n += 1
    print(f"{n}개 md 생성 → {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
