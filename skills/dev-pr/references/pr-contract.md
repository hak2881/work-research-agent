# Pull request creation report

Write the report in Korean unless requested otherwise. Report only observed repository, validation, push, and PR state.

```text
PR 생성 결과: created | reused | blocked
프로젝트·작업: <project / work-item key and title>
입력: <없음 | work-item key | Slack permalink>

대상 확인
- 저장소: <normalized remote>
- head: <branch@SHA>
- base: <branch and delivery-rule evidence>
- 작업 트리: <clean, checked time>

변경·검수
- 범위: <problem and resulting behavior from actual diff>
- 커밋: <included SHAs>
- 테스트: <commands and observed results at head SHA>
- 미확인·후속: <review, migration, deployment, production checks or 없음>

PR
- URL·번호: <URL / number>
- 상태: <open, review-ready>
- push: <remote branch@SHA verified>
- 중복 검사: <existing PR coverage and result>

DB 기록
- 이벤트·연결: <pr_created|pr_reused identifiers>
- 저장 실패: <reason or 없음>

병합·배포
- 병합: 실행하지 않음
- 배포: 실행하지 않음
- 작업 상태: verification_pending 유지
```

Use `created` only after rereading the PR and confirming its head, base, and URL. Use `reused` only for the same repository, head, base, and scope. Use `blocked` before push whenever work, target, history, validation, or PR identity is ambiguous.
