"""메일 초안이 rubric의 자동 검증 항목을 통과하는지 확인한다.

사용법:
    python verify_draft.py draft.md --count 4 [--customer 예시고객(주)]
통과하면 종료 코드 0, 실패 항목이 있으면 1.
"""
import argparse
import re
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--customer")
    a = ap.parse_args()

    text = open(a.draft, encoding="utf-8").read()
    fails = []

    m = re.search(r"총\s*\**\s*(\d+)\s*명", text)
    if a.count == 0:
        if "신규 등록자는 없습니다" not in text:
            fails.append("0명인데 '신규 등록자는 없습니다' 문구가 없음")
    elif not m:
        fails.append("본문에 '총 N명' 문구가 없음")
    elif int(m.group(1)) != a.count:
        fails.append(f"본문 인원수({m.group(1)}) != COUNT({a.count})")

    html_rows = len(re.findall(r"<tr>\s*<td", text))
    md_rows = len([l for l in text.splitlines()
                   if re.match(r"\|\s*\d+\s*\|", l)])
    rows = html_rows or md_rows
    if rows != a.count:
        fails.append(f"표 데이터 행 수({rows}) != COUNT({a.count})")

    if a.customer:
        subject = next((l for l in text.splitlines() if "제목" in l), "")
        if a.customer not in subject:
            fails.append(f"제목에 고객사명({a.customer}) 없음")

    left = re.findall(r"\{[^}\n]+\}", text)
    if left:
        fails.append(f"채워지지 않은 플레이스홀더: {left}")

    if fails:
        for f in fails:
            print("FAIL:", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
