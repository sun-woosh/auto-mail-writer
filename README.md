# 주간 대시보드 신규 등록 현황 메일 Skill

매주 수요일, 고객사에 **금주 신규 대시보드 등록자 인원수와 명단**을 보내는 메일 초안을 만들어 주는 Claude Skill입니다.
등록자 CSV를 주면 금주 대상자만 걸러 인원수를 세고, 명단을 **메일 본문 표**로 정리한 뒤 검증까지 마칩니다.

> 하네스 엔지니어링 과제: "LLM은 코어, 하네스는 코어를 감싸는 업무 환경" 구조 6가지를 적용했습니다.

## 왜 만들었나
- 매주 같은 메일을 반복해서 쓴다 (고객사, 인원수, 명단 표)
- 사람이 인원수를 세고 표를 옮기다 보면 **숫자와 표가 어긋나는 실수**가 생긴다
- 그래서 집계와 검증은 스크립트가, 문장 작성은 LLM이 맡도록 나눴다

## 사용 방법

### 1. 설치
```bash
git clone https://github.com/sun-woosh/auto-mail-writer.git "$env:USERPROFILE\.claude\skills\weekly-dashboard-report"
```
설치 후 Claude Code를 새로 시작합니다.

### 2. 입력 준비
대시보드 등록자를 CSV로 준비합니다. 필수 컬럼은 `이름`, `소속`, `등록일`입니다 ([예시](examples/sample_input.csv)).

### 3. 요청
```
이번 주 신규 등록자 메일 써줘. 파일은 C:\...\등록자.csv, 고객사는 OO(주)
```

### 4. 확인 후 직접 발송
Claude가 만든 초안을 확인하고 메일로 직접 보냅니다. 이 스킬은 **발송하지 않습니다.**

결과 예시는 [examples/sample_output.md](examples/sample_output.md)를 참고하세요.

## 하네스 6가지 구조 적용

| # | 구조 | 이 스킬에서의 구현 |
|---|---|---|
| 1 | **Role** | 기획자(입력 확인) · 생성자(초안 작성) · 평가자(검증)를 분리 → [roles.md](references/roles.md) |
| 2 | **Rubric** | 합격 기준 + 자동 검증 (인원수와 표 행 수 일치 등) → [rubric.md](references/rubric.md), [verify_draft.py](scripts/verify_draft.py) |
| 3 | **Context** | 고객사 정보, 지난주 인수인계 메모 → [customers.md](references/customers.md), [handoff.md](references/handoff.md) |
| 4 | **Tools** | 집계 스크립트, 검증 스크립트, CSV 파일 읽기 → [scripts/](scripts/) |
| 5 | **Workflow** | 계획 → 실행 → 검증 → 수정 피드백 루프 (최대 2회) → [SKILL.md](SKILL.md) |
| 6 | **Guardrail** | 발송 금지, CSV 외 개인정보 추가 금지, 승인 지점, 재시도 제한 → [guardrails.md](references/guardrails.md) |

## 폴더 구조
```
├── SKILL.md              # 스킬 진입점 (워크플로우)
├── README.md
├── scripts/
│   ├── make_table.py     # 금주 필터 + 인원수 + 메일용 표(HTML/마크다운)
│   └── verify_draft.py   # 초안 자동 검증 (PASS/FAIL)
├── templates/email.md    # 메일 템플릿 (기본 / 0명인 주)
├── references/           # roles, rubric, customers, handoff, guardrails
└── examples/             # 가상 입력·출력 샘플
```

## 스크립트 단독 실행
```bash
# 금주(월~발송일) 대상자 집계 + 표 생성
python scripts/make_table.py examples/sample_input.csv --date 2026-11-04

# 초안 검증
python scripts/verify_draft.py examples/sample_output.md --count 4 --customer "예시고객(주)"
```

## 참고
- `references/customers.md`와 `examples/`의 데이터는 모두 **가상**입니다. 실제 사용 시 본인 고객사 정보로 바꾸세요.
- "금주" 기준은 해당 주 월요일~발송일이며, `--start`/`--end`로 바꿀 수 있습니다.
