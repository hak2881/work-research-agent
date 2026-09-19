# LUKUKU policy contract

Write in Korean unless the user requests otherwise. The completed artifact is Markdown only and preserves the standard information architecture.

## Required structure

- Project title, document information, and change history.
- The eight areas in order: 회원, 상품, 주문, 클레임, CRM, 물류, 판매 채널, 정산 및 회계.
- A real `최종 검토일` for every area.
- Additional project-specific areas only after section 8.

Each area contains one or more `### 정책명` entries, `현재 확정된 정책 없음`, or `적용 대상 아님`.

- `agreed`: a current policy with explicit authoritative agreement, title, body, review date, and evidence.
- `no_confirmed_policy`: the area was reviewed and no current agreed policy was found. This is different from missing access or an incomplete search.
- `not_applicable`: an authoritative source explicitly excludes the area from the project.

Do not leave authoring comments, examples, `{placeholders}`, `YYYY-MM-DD`, proposed policy, open questions, estimates, schedules, implementation details, or test results in the completed file.

## Versions and changes

- Internal compiled versions begin at `v0.1`.
- `v1.0` requires explicit review of the compiled document.
- Every version has an immutable archive file and an explicit predecessor in history.
- Preserve unchanged current policies verbatim during a scoped revision.
- Reuse the same internal policy key across versions when the policy identity remains the same.
- Record added, changed, removed, and superseded policies in the change history. Removed and superseded text stays in prior snapshots, not in the current body.
- Update an area's review date only when that area was actually rechecked.

## Output

```text
정책 문서 작성 결과
- 프로젝트: <canonical project>
- 문서 버전: <version>
- 문서 상태: 내부 검토 | 검토 완료
- 검수 상태: 확인 완료 | 부분 확인 | 확인 불가
- 버전 보관 파일: <clickable path>
- 프로젝트 정책 파일: <clickable path | 대상 저장소 확인 필요>

이번 변경
- 추가·수정·삭제·변경 없음

문서에 반영하지 않은 내용
- <미합의, 충돌, 근거 부족 내용과 이유 | 없음>

PM 확인 필요
- <decision-changing question | 없음>
```

