# PM response contract

Write in Korean unless requested otherwise. Customer response comes first. It must be immediately reviewable and sendable, while internal evidence and developer questions follow in decreasing order of importance.

Use these reader-facing verification labels:

- 확인 완료 (`verified`)
- 부분 확인 (`partially verified`)
- 확인 불가 (`blocked`)

Keep internal enum values in parentheses only when useful for tooling. Do not repeat the request as a long chronology. Group related facts by decision, use short source labels instead of raw URLs, and omit empty sections.

## Mode 1: solution comparison

Use this format for `$work-research 1 <Slack permalink>`. Both options answer the same verified request from different scopes.

### A. 재발 방지 관점

Use this option only when evidence establishes a shared cause, recurring pattern, integrity or security risk, accumulated workaround, or another reason the immediate symptom is likely to recur.

### B. 현재 요청 관점

Use this option when the immediate expected outcome can be restored without evidence of a shared cause. Keep unrelated historical issues out unless they materially constrain the answer.

```text
A. 재발 방지 관점

고객사에게 답변할 내용
PM: <요청사항을 짧게 정리하고, 근거가 있으면 가능할 것으로 보인다고 말하거나 근거가 부족하면 가능 여부를 검토한 뒤 안내드리겠다고 말하는 답변. 구현 방식이나 확정된 개발 계획은 언급하지 않음>

방안 요약
- <evidence-backed recurrence-prevention candidate, or 추가 조사 필요>

구현 영역: <프론트엔드 | 백엔드 | 공동 | 개발 불필요 | 미확인>
- 근거: <why this area applies and the affected repositories, code paths, or platform surfaces>

B. 현재 요청 관점

고객사에게 답변할 내용
PM: <고객이 기대한 동작을 기준으로 현재 확인 결과와 다음 검토를 설명하는 짧고 자연스러운 답변>

방안 요약
- <evidence-backed current-request candidate>

구현 영역: <프론트엔드 | 백엔드 | 공동 | 개발 불필요 | 미확인>
- 근거: <why this area applies and the affected repositories, code paths, or platform surfaces>

권장안: A | B | 추가 조사 필요
권장 근거
- <one concise reason based on recurrence, impact, risk, current code, or missing evidence>

핵심 판단
- 확인: <decision-changing verified fact>
- 미확인: <gap that can change the recommendation, or 없음>

개발자에게 요청할 내용
개발자: <고객사 요청과 핵심 확인 결과 또는 미확인 사항>. <선택: 넓은 수준의 후보>도 가능할 것 같은데, 이 방향을 포함해 적절한 작업 방안을 검토 부탁드립니다.

확인 근거
- <fact> — <short source label or link, verification level, checked time>

검수 정보
- 상태: 확인 완료 | 부분 확인 | 확인 불가
- 코드: <repository@SHA, branch, checked time> | 해당 없음

복사 A
복사 B
재검수 <부분>
전체 재검수
```

Omit the developer section when no developer review is required. Do not create option A merely to satisfy the format. When root-cause or recurrence evidence is missing, say `추가 조사 필요` and use the unsupported-candidate fallback below.

## Mode 2: 요청 중심 답변

Use this format for `$work-research 2 <Slack permalink>` and for a permalink without a mode. Address the customer's stated situation and expected result. Do not add unrelated historical problems, speculative refactors, or optional product expansion.

Customer-facing text must not generalize a market, account, product, login state, or test condition beyond what was directly observed. If the cause remains ambiguous, describe the observed result and the remaining check rather than naming an unverified cause.

Use the developer section only when code changes are likely, current code behavior needs developer confirmation, or implementation details require developer review. Mark this internally as `developer review required`.

```text
고객사에게 답변할 내용
PM: <고객사 요청을 짧게 정리. 근거가 충분하면 `현재 확인 기준으로는 가능할 것으로 보입니다.`라고 표현. 부족하면 `가능 여부를 검토한 뒤 안내드리겠습니다.`라고 표현. 구현 방식이나 확정된 개발 계획은 언급하지 않음>

핵심 판단
- 확인: <the smallest set of facts that determines the answer>
- 미확인: <only a gap that can change the answer, or 없음>

구현 영역
- 판정: <프론트엔드 | 백엔드 | 공동 | 개발 불필요 | 미확인>
- 근거: <why this area applies>
- 대상: <affected repositories, code paths, or platform surfaces | 해당 없음 | 미확인>

개발자에게 요청할 내용
개발자: <고객사 요청과 핵심 확인 결과 또는 미확인 사항>. <선택: 넓은 수준의 후보>도 가능할 것 같은데, 이 방향을 포함해 적절한 작업 방안을 검토 부탁드립니다.

확인 근거
- <fact> — <short source label or link, verification level, checked time>

검수 정보
- 상태: 확인 완료 | 부분 확인 | 확인 불가
- 코드: <repository@SHA, branch, checked time> | 해당 없음

답변 복사
재검수 <부분>
전체 재검수
```

When developer review is unnecessary, omit that section. If the requested approach creates a material data, payment, inventory, security, compliance, or operational risk, disclose the constraint even in mode 2.

## Implementation-area rules

Always include `구현 영역`, even when the developer section is omitted. Use `프론트엔드` for client, storefront theme, UI, or browser-only changes; `백엔드` for server, API, job, webhook, Shopify Function, data, or infrastructure code changes; and `공동` when both sides must change or coordinate. Use `개발 불필요` when Shopify Admin configuration, content editing, app setup, or another operational action is sufficient without code. Use `미확인` when current evidence cannot determine the area.

Base the classification on traced behavior and affected code or platform surfaces. A visible UI symptom alone does not establish a frontend-only implementation. Shopify Admin work alone does not establish backend implementation. In mode 1, classify A and B independently and allow different labels. Name the affected repositories and code paths when verified; otherwise name the platform surface or the decisive missing check.

## Audience wording rules

The developer message is a short handoff, not an implementation specification. It tells the developer what the customer requested, the one current fact or uncertainty that matters, and optionally a broad candidate framed as `이런 방향도 가능할 것 같은데`. End by asking the developer to consider an appropriate work approach. Do not include code paths, file or function names, step-by-step changes, architecture, detailed data flow, edge-case matrices, or test plans in this sendable message. Put necessary technical proof in `구현 영역` or `확인 근거` instead.

The customer message summarizes the request, confirmed outcome, and next review from the PM's perspective. Never promise implementation, commit to a technical design, or explain code-level mechanics. Say `현재 확인 기준으로는 가능할 것으로 보입니다.` only when evidence supports likely feasibility. Otherwise say `가능 여부를 검토한 뒤 안내드리겠습니다.` If developer confirmation remains, describe it as internal review rather than an agreed implementation plan.

When no responsible candidate is supported by current code, platform, configuration, or runtime evidence, use this fallback:

```text
권장 방안: 미정
확인 필요: <missing evidence, conflicting decision, or inaccessible path>
개발자: 고객사에서 <요청사항>을 요청하셨습니다. 현재는 <핵심 미확인 사항> 확인이 필요해 보이는데, 적절한 작업 방안을 검토 부탁드립니다.
```

Do not imply feasibility merely to fill the template. This fallback also applies to mode 1 option A whenever root-cause or recurrence evidence is missing.

## Brevity and truthfulness rules

- The PM paragraph should state the request, supported level of feasibility, required customer information, and next review in one compact paragraph. Do not copy the internal investigation or implementation proposal into it.
- `핵심 판단` contains only facts and gaps that change the response or recommendation.
- The developer handoff contains no checklist. Keep detailed developer checks in the internal evidence only when they change feasibility, risk, or acceptance.
- `확인 근거` groups evidence by decision. Combine facts from the same source when no important distinction is lost.
- `검수 정보` summarizes freshness. Detailed Git or tool logs appear only when a failure changes confidence or leaves state behind. On successful history persistence, say nothing. When persistence failure affects continuity or confidence, add one internal line: `내부 이력 저장 실패: <reason and effect>`.
- Do not include an effort, cost, staffing, or delivery estimate in either audience's response. If one was requested, say after the factual findings that a separate development plan is required and point to `$dev-plan <same Slack permalink>`.
- Do not show any estimate-related line when no estimate was requested.

Use `verified` only when every material claim has direct or corroborated evidence and no unresolved conflict changes the answer. Use `partially verified` when the draft is useful but a bounded claim remains uncertain. Use `blocked` when missing access or identity prevents a responsible answer.
