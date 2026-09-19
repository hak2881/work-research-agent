# LUKUKU WBS contract

Write in Korean unless the user requests another language. Keep the document proportional to the selected scope while preserving the standard information architecture.

## Schedule fields

- **Baseline:** explicitly agreed original dates. Once approved, a later WBS version repeats the same values.
- **Forecast:** latest expected dates for incomplete work. A change requires source evidence and a change note.
- **Actual:** directly observed execution dates. Partial execution may have an actual start with no end.
- **Schedule basis:** `confirmed | planned | proposed | unknown`.

Proposed dates never appear as confirmed baseline dates. Unknown dates are `미정`, stay in detailed rows, and are omitted from date-based charts with a visible note.

## Work and status

Display statuses are `예정 | 진행 중 | 확인 대기 | 완료 | 보류`.

- `완료` requires accepted completion criteria and result evidence.
- `확인 대기` means an external decision or verification is pending.
- `보류` requires explicit deferral or hold evidence.
- Cancelled and superseded items are historical, not active rows.

Tasks and milestones use stable display IDs within one WBS lineage. Durable database work-item keys remain the identity used for dependencies and source links.

## Effort

Preserve ranges and units. Keep source and engineering estimates separate in history and select the exact estimate record used by the WBS. Do not sum incompatible units.

Missing effort is blank or `미입력`; verified zero is numeric `0`. Milestones have zero effort and are excluded from task and effort totals. Unapproved additions are excluded from confirmed totals.

Actual accumulated effort does not determine progress percentage and does not establish billing.

## Required manifest content

The canonical manifest contains:

- Template and document versions, number, status, as-of date, project, customer, PM, author, and predecessor.
- Bounded scope, exclusions, and unresolved additions.
- Change history and primary sources with versions and checked times.
- Work items and milestones with durable and display IDs.
- Owner, collaborators, phase, workstream, origin, confirmed-scope flag, and status.
- Baseline, forecast, and actual periods with sources.
- Selected estimate, actual effort, dependencies, prerequisites, criteria, requirement references, result evidence, change note, and next action.
- Calendar display range and timezone.

## Versions

- Internal draft: `v0.1`, then `v0.2` and so on.
- First explicitly approved sharing version: `v1.0`.
- Later shared revisions: `v1.1`, `v1.2`, and so on.
- Template version `1.1` is separate from the project document version.

Every revision preserves its predecessor and records affected IDs, reason, author, confirmation state, and source. Generation and silence do not approve a version.

## Output response

```text
WBS 작성 결과
- 프로젝트: <canonical project>
- 대상 범위: <bounded scope>
- 현황 기준일: <date>
- 문서 상태: 초안 | 검토 중 | 확정 | 보류
- 검수 상태: 확인 완료 | 부분 확인 | 확인 불가
- XLSX: <clickable local path | 생성 실패 이유>
- PDF: <clickable local path | 생성 실패 이유>

먼저 확인할 항목
- <overdue, waiting, unscheduled, unresolved, or 없음>

근거 범위
- <source, version, checked time>

다음 단계
- 확정된 착수 대상만 `$dev-implement <work-item key>`로 진행
```

The response does not authorize implementation, publish files, or claim customer approval.
