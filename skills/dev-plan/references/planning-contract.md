# Development planning report

Write in Korean unless requested otherwise. Keep sourced facts, engineering proposals, and unanswered questions visibly separate.

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
