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
PM: <재발 가능성과 함께 연관된 처리 과정을 검토한다는 짧고 자연스러운 답변>

방안 요약
- <evidence-backed recurrence-prevention candidate, or 추가 조사 필요>

B. 현재 요청 관점

고객사에게 답변할 내용
PM: <고객이 기대한 동작을 기준으로 현재 확인 결과와 다음 검토를 설명하는 짧고 자연스러운 답변>

방안 요약
- <evidence-backed current-request candidate>

권장안: A | B | 추가 조사 필요
권장 근거
- <one concise reason based on recurrence, impact, risk, current code, or missing evidence>

핵심 판단
- 확인: <decision-changing verified fact>
- 미확인: <gap that can change the recommendation, or 없음>

개발자에게 요청할 내용
- 현재 확인: <verified current behavior and constraint>
- 권장 방안: <candidate and why it is plausible, or 미정>
- 꼭 확인할 항목:
  - <implementation feasibility, better alternative, affected area, or decisive test>

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
PM: <검수 후 바로 보낼 수 있는 concise answer; no internal tools, SHAs, access errors, or DB details>

핵심 판단
- 확인: <the smallest set of facts that determines the answer>
- 미확인: <only a gap that can change the answer, or 없음>

개발자에게 요청할 내용
- 현재 확인: <verified behavior and evidence boundary>
- 권장 방안과 근거: <one evidence-backed candidate, or 미정>
- 꼭 확인할 항목:
  - <feasibility or a better approach>
  - <affected surface or decisive verification scenario>

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

## Developer recommendation rules

The developer message must distinguish verified current behavior from a proposed implementation. Present the recommended approach as a candidate for developer review, not an approved design. Give one recommendation, its evidence boundary, and only the checks that can change the decision. Ask whether the approach has 구현 가능성 and whether a 더 적합한 방안 exists; end the request naturally with `검수 부탁드립니다.` Do not present a proposal as an approved requirement or completed work.

When no responsible candidate is supported by current code, platform, configuration, or runtime evidence, use this fallback:

```text
권장 방안: 미정
확인 필요: <missing evidence, conflicting decision, or inaccessible path>
개발자: 현재 근거만으로는 구현 방향을 제안하기 어렵습니다. 구현 가능성과 더 적합한 방안이 있는지 검수 부탁드립니다.
```

Do not imply feasibility merely to fill the template. This fallback also applies to mode 1 option A whenever root-cause or recurrence evidence is missing.

## Brevity and truthfulness rules

- The PM paragraph should state the conclusion, required customer information, and next review in one compact paragraph. Do not copy the internal investigation into it.
- `핵심 판단` contains only facts and gaps that change the response or recommendation.
- `꼭 확인할 항목` contains only developer checks that can change feasibility, design, risk, or acceptance. Do not turn every observed detail into a checklist.
- `확인 근거` groups evidence by decision. Combine facts from the same source when no important distinction is lost.
- `검수 정보` summarizes freshness. Detailed Git or tool logs appear only when a failure changes confidence or leaves state behind. On successful history persistence, say nothing. When persistence failure affects continuity or confidence, add one internal line: `내부 이력 저장 실패: <reason and effect>`.
- Do not include an effort, cost, staffing, or delivery estimate in either audience's response. If one was requested, say after the factual findings that a separate development plan is required and point to `$dev-plan <same Slack permalink>`.
- Do not show any estimate-related line when no estimate was requested.

Use `verified` only when every material claim has direct or corroborated evidence and no unresolved conflict changes the answer. Use `partially verified` when the draft is useful but a bounded claim remains uncertain. Use `blocked` when missing access or identity prevents a responsible answer.
