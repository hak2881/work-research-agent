# PM response contract

Write in Korean unless requested otherwise. Customer-facing text should describe the observed situation, expected outcome, and next review naturally. Keep internal mechanics out of that text unless they affect the decision.

## Mode 1: solution comparison

Use this format for `$work-research 1 <Slack permalink>`. Both options use the same verified request and evidence but answer different decision questions.

### A. 재발 방지 관점

Use this option when current evidence establishes a shared cause, recurring pattern, integrity or security risk, accumulated workaround, or another reason that correcting the immediate symptom would likely recur. If the root cause is not established, state that this option requires further investigation instead of inventing a structural change.

```text
A. 재발 방지 관점

고객사에게 답변할 내용
PM: <문의한 현상과 함께 동일 유형의 문제가 반복되지 않도록 연관된 처리 과정도 검토한다는 자연스러운 답변>

개발자에게 요청할 내용
개발자: <검증된 현재 동작, 직접 원인, 재발 근거와 가능한 해결 방향을 구분하고 검수를 요청하는 내용>

적용 근거
- 확인된 원인: <directly verified cause or 미확인>
- 재발·공통 영향: <evidence or 확인 필요>
- 예상 영향 범위: <components/data/operations with evidence>
- 완료 조건: <observable checks>
```

### B. 현재 요청 관점

Use this option when the observed issue is local or the immediate requested outcome can be restored without evidence of a shared cause. Describe the customer's expected behavior positively. Keep broader historical issues out unless they materially constrain this answer.

```text
B. 현재 요청 관점

고객사에게 답변할 내용
PM: <문의한 상황에서 기대한 동작이 정상적으로 이루어질 수 있도록 현재 동작과 필요한 변경사항을 검수한다는 자연스러운 답변>

개발자에게 요청할 내용
개발자: <고객이 제시한 발생 조건, 현재 동작, 기대 결과, 필요한 변경 방향과 검수 시나리오>

적용 근거
- 발생 조건: <verified trigger>
- 기대 결과: <explicit requested outcome>
- 확인된 변경 범위: <evidence-backed code/configuration surface>
- 완료 조건: <observable checks>
```

After both options, provide one decision block and shared evidence:

```text
권장안: A | B | 추가 조사 필요
권장 근거
- <recurrence, blast radius, risk, current code, history, or missing evidence>

확인 근거
- <fact> — <source label, URI/reference, verification level, checked time>

확실하지 않은 부분
- <missing access, conflicting evidence, assumption, or 없음>

검수 상태: verified | partially verified | blocked
확인한 코드: <repository>@<SHA> | 해당 없음

복사 A
복사 B
재검수 <부분>
전체 재검수
```

Do not create option A merely to satisfy the format. When evidence supports only option B, option A should explain which causal evidence is missing and why a recurrence-prevention proposal cannot yet be responsibly drafted.

## Mode 2: 요청 중심 답변

Use this format for `$work-research 2 <Slack permalink>` and for a permalink without a mode. Address the customer's stated situation and expected result. Do not add unrelated historical problems, speculative refactors, or optional product expansion.

Use the dual-audience format when code changes are likely, the current code behavior needs developer confirmation, or implementation details require developer review. Mark this internally as `developer review required`.

```text
개발자에게 요청할 내용
개발자: <고객이 제시한 발생 조건과 기대 동작, 확인된 현재 동작, 필요한 변경 방향을 설명하고 검수를 요청하는 내용>

확인할 사항
- <관련 코드 경로, 제약, 데이터, 설정, 배포 여부 또는 검수 시나리오>

고객사에게 답변할 내용
PM: <문의한 상황과 기대 동작을 기준으로 현재 동작과 필요한 변경사항을 검수한 뒤 안내한다는 자연스러운 답변>

확인 근거
- <fact> — <source label, URI/reference, verification level, checked time>

확실하지 않은 부분
- <missing access, conflicting evidence, assumption, or 없음>

검수 상태: verified | partially verified | blocked
확인한 코드: <repository>@<SHA> | 해당 없음

답변 복사
재검수 <부분>
전체 재검수
```

When developer review is unnecessary, omit the developer section and start with the customer response. If the requested approach creates a material data, payment, inventory, security, compliance, or operational risk, disclose the constraint even in mode 2; request-focused does not mean hiding a decision-changing risk.

## Shared truthfulness rules

The developer message must distinguish verified current behavior from a proposed implementation. Prefer language such as `현재 코드 기준으로 <방식>으로 구현할 수 있을 것으로 보입니다. <확인할 사항> 검수 부탁드립니다.` Do not present a proposal as an approved requirement or completed work.

The customer message must avoid promising feasibility, schedule, scope, or completion before the required review. Use `verified` only when every material claim has direct or corroborated evidence and no unresolved conflict changes the answer. Use `partially verified` when the draft is useful but a bounded claim remains uncertain. Use `blocked` when missing access or identity prevents a responsible answer.
