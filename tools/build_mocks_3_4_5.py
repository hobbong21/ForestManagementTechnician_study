# -*- coding: utf-8 -*-
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base_dir = os.path.join(ROOT, "04_예상문제")
out_dir = os.path.join(ROOT, "05_모의고사")

# Partition definitions
mock_partitions = {
    3: {
        "title": "03. 산림경영지도원 전과목 실전모의고사 100제 (제3회 기본·핵심 집중 실전 150분 대비)",
        "desc": "기본 개념과 빈출 핵심 조항을 집중적으로 다루어 합격 안전권(60~70점)을 확보하는 제3회 실전모의고사입니다.",
        "q_ids": {
            1: [2, 4, 5, 7, 9, 10, 11, 13, 15, 16, 18, 19, 20, 22, 23, 24, 26, 27, 28, 29],
            2: [2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 19, 21, 22, 23, 25, 26, 27, 29],
            3: [1, 3, 4, 6, 7, 9, 10, 12, 13, 14, 16, 17, 19, 20, 21, 23, 24, 25, 27, 28],
            4: [2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 18, 19, 20, 22, 23, 24, 25, 27],
            5: [1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15, 16, 17, 19, 20, 21, 23, 24, 25, 26],
            6: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        }
    },
    4: {
        "title": "04. 산림경영지도원 전과목 실전모의고사 100제 (제4회 심화·응용 완성 실전 150분 대비)",
        "desc": "개정 법령, 최신 정책 기준 및 산림기사 응용 심화 문제를 집중 점검하여 상위 10% 고득점을 노리는 제4회 실전모의고사입니다.",
        "q_ids": {
            1: [31, 32, 33, 34, 36, 37, 38, 39, 40, 67, 68, 69, 70, 71, 73, 74, 76, 78, 79, 80],
            2: [30, 31, 32, 34, 35, 36, 38, 39, 40, 66, 68, 69, 70, 71, 73, 74, 76, 77, 79, 80],
            3: [29, 30, 32, 33, 34, 35, 37, 38, 39, 64, 66, 67, 68, 69, 73, 75, 76, 77, 78, 80],
            4: [28, 29, 31, 32, 33, 34, 36, 37, 38, 40, 45, 48, 49, 69, 70, 73, 74, 76, 77, 78],
            5: [28, 29, 30, 32, 33, 34, 35, 37, 38, 39, 65, 66, 67, 69, 70, 71, 73, 75, 78, 79],
            6: [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
        }
    },
    5: {
        "title": "05. 산림경영지도원 전과목 실전모의고사 100제 (제5회 실무·신출제기준 파이널 150분 대비)",
        "desc": "산림사업 현장 실무 및 2026 최신 산림기사·지도원 신유형 문제를 총망라한 파이널 실전모의고사입니다.",
        "q_ids": {
            1: list(range(81, 101)),
            2: list(range(81, 101)),
            3: list(range(81, 101)),
            4: list(range(81, 101)),
            5: list(range(81, 101)),
            6: list(range(81, 101))
        }
    }
}

subjects_info = [
    (1, "제1과목: 조림학", "01_조림_예상문제.md"),
    (2, "제2과목: 산림보호학", "02_산림보호_예상문제.md"),
    (3, "제3과목: 임업경영학", "03_산림경영_예상문제.md"),
    (4, "제4과목: 산림관계법규", "04_산림관계법규_예상문제.md"),
    (5, "제5과목: 산림토목학(임도·사방)", "05_산림토목(임도·사방)_예상문제.md"),
    (6, "[부록: 선택과목 대비] 제5과목 대체: 임산가공학", "06_임산가공_예상문제.md")
]

# Read all question blocks
all_blocks = {}
for s_num, s_title, fname in subjects_info:
    path = os.path.join(base_dir, fname)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    blocks = re.split(r"\n(?=\*\*\d+\.\*\*)", text)
    block_dict = {}
    for b in blocks:
        m = re.search(r"\*\*(\d+)\.\*\*", b)
        if m:
            block_dict[int(m.group(1))] = b.strip()
    all_blocks[s_num] = block_dict

for m_num, m_info in mock_partitions.items():
    out_fname = f"0{m_num}_전과목_실전모의고사_100제.md"
    out_path = os.path.join(out_dir, out_fname)
    lines = []
    lines.append(f"# 💯 [05_모의고사] {m_info['title']}\n\n")
    lines.append(f"> {m_info['desc']}\n")
    lines.append("> 2026 산림경영지도원 자격전형 필기시험과 동일한 구성(필수 4과목 + 선택 1과목, 과목당 20문항, 총 100문항, 150분)입니다.\n")
    lines.append("> 모든 문제는 **1문 1답(문제 ➔ 정답 & 상세해설 & 출제근거)**으로 바로 이어져 편리하고 빠른 실전 피드백이 가능합니다.\n")
    lines.append("> (※ 선택과목으로 임산가공을 선택하는 수험생을 위해 **[선택 제5과목 대체: 임산가공학 20문항]**도 부록으로 함께 수록되어 있습니다.)\n\n---\n")
    
    global_q_idx = 1
    for s_num, s_title, fname in subjects_info:
        is_appendix = (s_num == 6)
        lines.append(f"\n## {s_title}\n\n")
        q_ids = m_info["q_ids"][s_num]
        sub_q_idx = 1
        for qid in q_ids:
            b_content = all_blocks[s_num][qid]
            b_content = re.sub(r"\n+---+\s*$", "", b_content).strip()
            if not is_appendix:
                q_label = f"**[문제 {global_q_idx:03d}] (원문 #{qid})**"
                global_q_idx += 1
            else:
                q_label = f"**[선택문제 {sub_q_idx:03d}] (원문 #{qid})**"
            sub_q_idx += 1
            
            b_mod = re.sub(r"^\*\*\d+\.\*\*", q_label, b_content)
            lines.append(b_mod + "\n\n---\n\n")
            
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Generated {out_fname} with 100 questions + 20 appendix questions.")

print("Mocks 3, 4, 5 successfully generated!")
