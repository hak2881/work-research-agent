# Development planning report

Write in Korean unless requested otherwise. Keep sourced facts, engineering proposals, and unanswered questions visibly separate. The first section is always the PM-facing result. For a simple review, the detailed report follows inline. For a complex review, the complete detailed report belongs in the linked HTML and the session contains only the PM conclusion, link, and an optional short internal status.

## Simple review

```text
PM에게 전달할 내용
PM: <검토 결론과 PM이 알아야 할 다음 행동을 바로 전달할 수 있는 짧은 답변>

추가 확인 질문
- <question, reason, and development impact>
```

When no additional answer or decision is needed, write `추가 없음` explicitly and briefly name what was reviewed. Do not expose internal tool mechanics, database operations, or speculative implementation details in the sendable text.

## Complex review

Return a short session response before the detailed planning report:

```text
PM에게 전달할 내용
PM: <핵심 결론, 중요한 추가 질문 또는 다음 결정>

상세 검토 보고서: <clickable local HTML link>
```

The linked HTML carries every field from the internal planning report in addition to the source comparison, findings, reasons, development impact, options, and evidence. The session response must still state the decision; do not make the user open the file merely to learn the conclusion. If the HTML cannot be created and visually verified, identify the failure and return the full internal planning report inline.

## Internal planning report

```text
프로젝트: <canonical project>
입력 문서: <type, title, version/hash, URI, checked time>
계획 검수 상태: verified | partially_verified | blocked

요청 및 목표
- <explicit source requirement> — <source>

현재 동작·과거 결정
- <current repository@SHA behavior or sourced decision>
- <superseded or conflicting decision>

개발 가능성
- 판정: 가능 | 조건부 가능 | 현재 불가 | 미확인
- 근거: <code/platform/infrastructure evidence>

요구사항 충돌·질문
- <conflict or missing decision and why it changes the plan>

작업 계획
- <key> <explicit|proposed> <planned|ready|blocked>: <title>
  - 완료 조건: <explicit|proposed, accepted|proposed, observable check, source>
  - 선행 작업: <keys or 없음>
  - 담당 영역: <backend/frontend/Shopify/infrastructure/etc.>

공수 범위와 근거
- 출처 공수: <supplied estimate, provenance, or 없음>
- 엔지니어링 공수: <minimum–maximum unit and confidence, or 미산정 with blocking decision>
- 포함·제외·전제: <scope boundaries>

진행 기준
- 기준 범위: <authoritative PRD/WBS scope or 없음>
- 확인된 상태: <counts only when the denominator is authoritative>
- 미확인·제안 항목: <items excluded from progress>

DB 저장 결과
- 문서: <keys>
- 작업: <created/updated keys and origin/state>
- 저장 실패: <reason or 없음>

다음 단계
- <$dev-implement ready-key, required answer, or 없음>
```

Use `verified` only when the project, current behavior, material dependencies, and estimate inputs are sourced. Use `partially_verified` when the plan is useful but bounded by disclosed gaps. Use `blocked` when missing identity or a critical decision prevents a responsible work plan.
