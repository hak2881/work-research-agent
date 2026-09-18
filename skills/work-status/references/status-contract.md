# Project status contract

Write the report in Korean unless requested otherwise. Prefer concrete items and evidence over narrative. Omit an empty section only when its absence cannot be mistaken for missing coverage.

```text
프로젝트: <canonical project name>
상태 확인 시각: <timezone-aware time>

현재 요약
- <what is currently established, including the latest meaningful change>

완료된 작업
- <work item> — <Slack/PR/commit/deployment/acceptance evidence and time>

진행 중
- <explicit active work, owner when sourced, and next known checkpoint>

차단·확인 필요
- <blocker, conflict, missing access, decision, developer review, or 없음>

상태 미확인
- <item whose current state is not established, missing evidence, and what would resolve it>

최근 결정
- <decision or replacement> — <source and time>

관련 코드
- <repository@SHA> — <branch/default-branch relationship, dirty state, checked time; one line for every mapped repository>
- <unchecked repository> — <why it could not be inspected and effect on the report>

데이터 범위
- DB 기존 최신 근거: <pre-refresh time>
- Slack 이전 확인 지점: <per channel/source time or 없음>
- 새로 확인 완료한 Slack 범위: <per channel/source checked-through time or unavailable>
- 확인한 저장소: <count and names>
- 접근 불가·미확인: <sources and effect on conclusion or 없음>

다음 단계
- <evidence-backed next action, `$work-act <scope>`, `$work-research <Slack link>`, or 없음>

검수 상태: verified | partially verified | blocked
```

Use `verified` only when the project identity and every material status statement have direct or corroborated current evidence. Use `partially verified` when the report is useful but bounded freshness or access gaps remain. Use `blocked` when project identity or missing critical sources prevents a responsible status report.

Do not add a percentage unless an authoritative scope defines the denominator. When such a scope exists, report `확인된 완료 항목 X/Y` and list uncertain items instead of implying precision beyond the evidence.
