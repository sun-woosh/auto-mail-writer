"""등록자 CSV에서 금주 대상자를 걸러 인원수와 표를 출력한다.

사용법:
    python make_table.py input.csv [--date 2026-11-04] [--start 2026-11-02 --end 2026-11-04]
출력: 첫 줄 `COUNT=<n>`, 이후 HTML 표 (메일 본문용), 마지막에 마크다운 표.
"""
import argparse
import csv
import sys
from datetime import date, timedelta
from html import escape

COLUMNS = ["이름", "국가", "등록일"]


def parse(d: str) -> date:
    return date.fromisoformat(d.strip().replace(".", "-").replace("/", "-"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--date", help="발송일 (기본: 오늘)")
    ap.add_argument("--start", help="집계 시작일 (기본: 발송일이 속한 주의 월요일)")
    ap.add_argument("--end", help="집계 종료일 (기본: 발송일)")
    a = ap.parse_args()

    send = parse(a.date) if a.date else date.today()
    start = parse(a.start) if a.start else send - timedelta(days=send.weekday())
    end = parse(a.end) if a.end else send

    with open(a.csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            print(f"ERROR: 필수 컬럼 없음: {missing}", file=sys.stderr)
            return 1
        rows = [r for r in reader if start <= parse(r["등록일"]) <= end]

    rows.sort(key=lambda r: parse(r["등록일"]))
    print(f"COUNT={len(rows)}")
    print(f"PERIOD={start}~{end}")
    if not rows:
        return 0

    print("<table border='1' cellpadding='6' style='border-collapse:collapse'>")
    print("<tr>" + "".join(f"<th>{c}</th>" for c in ["번호"] + COLUMNS) + "</tr>")
    for i, r in enumerate(rows, 1):
        cells = [str(i)] + [escape(r[c].strip()) for c in COLUMNS]
        print("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    print("</table>")

    print()
    print("| 번호 | " + " | ".join(COLUMNS) + " |")
    print("|---|" + "---|" * len(COLUMNS))
    for i, r in enumerate(rows, 1):
        print(f"| {i} | " + " | ".join(r[c].strip() for c in COLUMNS) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
