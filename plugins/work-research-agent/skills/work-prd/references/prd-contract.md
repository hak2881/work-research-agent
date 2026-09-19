# LUKUKU PRD contract

Write in Korean unless the user requests another language. Preserve the standard section order and table meanings. Keep the document proportional to the selected scope; add rows and pages only when evidence requires them.

## Document status and versions

- Default status: `초안`
- Requirement state: `확정 | 확인 필요 | 보류`
- Never overwrite a previous version.
- Change history identifies affected FR IDs, the change and reason, and the reviewer or decision source.
- Version succession follows explicit version lineage for the same document number and bounded scope. Do not select a predecessor only because it has the highest version elsewhere in the project.

## Required sections

### 1. 문서 정보

Project, customer, author, version, date, document status, bounded target scope, document number, and change history.

### 2. 배경과 목표

Describe the verified current problem without a long chronology. Each goal includes the customer or user result and a way to confirm that result.

### 3. 포함·제외 범위

State concrete actors, targets, conditions, and behavior. Use excluded scope only for a real adjacent boundary; do not pad the document with unrelated ideas.

### 4. 사용자와 주요 업무 흐름

Identify roles, purposes, and work. Each flow has a start condition, ordered actors and actions, results, and material branches or exceptions. Distinguish manual, automatic, and system actions.

### 5. 기능 요구사항

Each `FR-NNN` states actor, condition, action, and result. Give it a sourced priority when available, a state, and an observable completion criterion. When the authoritative source does not define the criterion, write a proposed completion criterion prefixed with `[제안·확인 필요]`, keep the requirement state `확인 필요`, link the proposal to the gap that motivated it, and repeat the decision in section 7.2. The detailed view covers prerequisites, normal behavior, exception behavior, and related policy or screens.

Section 5.3 is optional technical context. Use it only for a verified existing system boundary, approved technical decision, or necessary integration constraint. Do not turn an engineering idea into a product requirement.

### 6. 품질·제약 조건

Create `NFR-NNN` entries only for relevant, sourced security, privacy, permission, performance, reliability, accessibility, or operational conditions. State the environment and observable judgment standard. Separate immutable constraints from unresolved choices.

### 7. 선행 조건·미확정 사항

List customer materials, accounts, permissions, integration preparation, owners, needed stage, and impact when missing. Every unresolved decision includes the affected scope or FR IDs, decision owner, and agreed date only when a date was explicitly supplied.

### 8. 전체 인수 기준·관련 문서

Define acceptance for the selected scope, connected business flows, and handoff or operational readiness. When an authoritative source does not explicitly define an acceptance criterion, prefix the proposed criterion with `[제안·확인 필요]`, connect it to the affected FR IDs, and repeat the decision in section 7.2. Do not present a renderer-required row as approved scope. Link each related policy, design, verification plan, or technical document to its relevant section or FR IDs with a version or checked date.

## Output response

```text
PRD 작성 결과
- 프로젝트: <canonical project>
- 대상 범위: <bounded scope>
- 문서 상태: 초안 | 검토 중 | 확정 | 보류
- 검수 상태: 확인 완료 | 부분 확인 | 확인 불가
- HTML: <clickable local path>
- PDF: <clickable local path | 생성 실패 이유>

PM 확인 필요
- <decision-changing unanswered question or 없음>

근거 범위
- <Slack/document/code/platform source with version or checked time>

다음 단계
- PRD 검토 후 `$dev-plan <PRD path>`
```

Do not include an effort estimate, developer task plan, implementation approval, or claim that rendering means the requirements are approved.
