# PM response contract

Write in Korean unless requested otherwise. The first paragraph must be suitable for the PM to send after review. Keep internal mechanics out of the sendable paragraph unless they affect the decision.

```text
PM: <customer-facing or internal sendable answer>

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

