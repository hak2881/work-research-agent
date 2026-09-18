# Developer implementation report

Write in Korean unless requested otherwise. Report observations from the actual worktree and history records; do not imply merge, deployment, or production completion.

```text
프로젝트·작업: <project> / <work-item key and title>
입력: <work-item key or Slack thread permalink>
Slack 연결: <root/replies linked to work item, or 해당 없음>
개발 상태: blocked | in_progress | verification_pending

착수 기준
- 문서: <accepted versions/hashes>
- 기준 아키텍처: <snapshot/version and source refs>
- 저장소: <repository@starting-SHA, branch, fetched default SHA, dirty state, checked time>
- 선행 작업·완료 조건: <resolved dependencies and accepted criteria>

히스토리 일치 검수
- 일치: <current implementation decisions supported by PRD/Slack/history>
- 충돌·대체됨: <superseding evidence or 없음>
- 접근 불가·미확인: <coverage gap and effect or 없음>

구현 내용
- <file/symbol and behavior changed>
- 커밋: <repository@SHA or uncommitted with reason>

완료 조건별 검수
- <criterion key> <accepted>: <test/inspection, expected, observed, pass|fail|unverified, evidence>
- 제안 조건: <not implemented, accepted separately, or 없음>

테스트
- <command/scenario>: <result and observation time>

DB 저장
- 이벤트·커밋·근거: <stored identifiers>
- 저장 실패: <reason or 없음>

남은 단계
- <review/PR/merge/deployment/acceptance evidence required for completed>
- `$b-end` 실행: 하지 않음
- `$b-deploy` 실행: 하지 않음
```

Use `verification_pending` only when the scoped implementation and its code-level checks pass. Use `blocked` when evidence or repository safety prevents edits. Never use `completed` in this workflow.
