# PM response contract

Write in Korean unless requested otherwise. Keep internal mechanics out of customer-sendable text unless they affect the decision.

## Choose the output mode

Use the dual-audience format when code changes are likely, the current code behavior needs developer confirmation, or implementation details require developer review. Mark this internally as `developer review required`.

Use the single customer format when the request can be answered from verified history, current behavior, Shopify capability, or other evidence without developer action.

## Developer review required

```text
개발자에게 요청할 내용
개발자: <현재 확인한 동작과 근거를 설명하고, 가능한 구현 방향을 제안한 뒤 검수를 요청하는 내용>

확인할 사항
- <개발자가 확인해야 할 코드 경로, 제약, 데이터, 배포 여부 또는 질문>

고객사에게 답변할 내용
PM: 문의해 주신 내용은 개발 확인이 필요한 사항입니다. 내부에서 현재 동작과 구현 가능 여부를 확인한 뒤 다시 안내드리겠습니다.

확인 근거
- <fact> — <source label, URI/reference, verification level, checked time>

확실하지 않은 부분
- <missing access, conflicting evidence, assumption, or 없음>

검수 상태: verified | partially verified | blocked
확인한 코드: <repository>@<SHA> | 해당 없음

1. 답변 복사
2. <부분> 재검수
3. 전체 독립 재검수
```

The developer message must distinguish verified current behavior from a proposed implementation. Prefer language such as `현재 코드 기준으로 <방식>으로 구현할 수 있을 것으로 보입니다. <확인할 사항> 검수 부탁드립니다.` Do not present a proposal as an approved requirement or completed work.

The customer message must avoid promising feasibility, schedule, scope, or completion before developer review. It should say that the request involves development and that the team will respond after checking it.

## No developer review required

```text
PM: <customer-sendable answer>

확인 근거
- <fact> — <source label, URI/reference, verification level, checked time>

확실하지 않은 부분
- <missing access, conflicting evidence, assumption, or 없음>

검수 상태: verified | partially verified | blocked
확인한 코드: <repository>@<SHA> | 해당 없음

1. 답변 복사
2. <부분> 재검수
3. 전체 독립 재검수
```

Use `verified` only when every material claim has direct or corroborated evidence and no unresolved conflict changes the answer. Use `partially verified` when the draft is useful but a bounded claim remains uncertain. Use `blocked` when missing access or identity prevents a responsible answer.
