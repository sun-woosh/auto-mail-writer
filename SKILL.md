---
name: weekly-dashboard-report
description: 매주 수요일 고객사에 보내는 "금주 신규 대시보드 등록자" 메일 초안을 만든다. 등록자 목록(CSV)을 받아 금주 대상자만 걸러 인원수를 세고, 본문에 표로 정리한 메일을 작성하고 검증까지 한다. "주간 등록 현황 메일", "수요일 고객사 메일", "신규 등록자 리스트 보내기" 요청에 사용.
---

# 주간 대시보드 신규 등록 현황 메일

매주 수요일, 고객사에 금주 신규 등록자 인원수와 명단을 표로 보낸다.
하네스 6가지 구조로 설계했다. LLM은 글쓰기만 맡고, 계산·검증·권한은 하네스가 맡는다.

| # | 구조 | 이 스킬에서의 구현 |
|---|---|---|
| 1 | Role | 기획자 · 생성자 · 평가자 분리 → `references/roles.md` |
| 2 | Rubric | 합격 기준 + 자동 검증 → `references/rubric.md`, `scripts/verify_draft.py` |
| 3 | Context | 고객사 정보 + 지난주 인수인계 → `references/customers.md`, `references/handoff.md` |
| 4 | Tools | 집계·검증 스크립트, CSV 파일 읽기 → `scripts/` |
| 5 | Workflow | 계획 → 실행 → 검증 → 수정 루프 (아래) |
| 6 | Guardrail | 발송 금지, 개인정보 제한, 승인 → `references/guardrails.md` |

## 입력
- 등록자 목록 CSV (필수 컬럼: `이름`, `국가`, `등록일`). `examples/sample_input.csv` 참고.
- 고객사명 (`references/customers.md`에 있으면 생략 가능)
- 발송일 (기본: 오늘)

## Workflow

1. **계획 (기획자)**: 입력 컬럼, 고객사, 발송일을 확인한다. 부족하면 추측하지 말고 되묻는다. `references/handoff.md`에서 지난주 정보를 읽는다.
2. **실행 (생성자)**: `python scripts/make_table.py <csv> --date <발송일>`로 인원수와 표를 얻고, `templates/email.md`에 채워 초안을 만든다. 인원수는 직접 세지 않는다.
3. **검증 (평가자)**: 초안을 파일로 저장해 `python scripts/verify_draft.py <초안> --count <COUNT>`를 실행하고, `references/rubric.md`의 수동 항목도 대조한다.
4. **수정**: 실패 항목만 고쳐 3번으로 돌아간다. 최대 2회 반복하고, 그래도 실패하면 실패 항목을 그대로 사용자에게 알린다.
5. **인수인계**: 통과한 초안과 확인 필요 사항(0명, 지난주 대비 급증·급감 등)을 사용자에게 보여주고, `references/handoff.md`에 이번 주 결과를 기록할지 묻는다.

## 핵심 규칙
- 발송은 하지 않는다. 사용자가 직접 보낸다. (`references/guardrails.md`)
- 0명인 주는 `templates/email.md`의 0명 버전을 쓴다.
- "금주"는 해당 주 월요일~발송일이다. 다른 기준이면 `--start`/`--end`로 지정한다.
