# Developer context report

Write in Korean unless requested otherwise. Keep desired, configured, deployed, and live states separate and attach a source reference and checked time to every material conclusion.

````text
프로젝트: <canonical project>
확인 시각: <timezone-aware time>
검수 상태: verified | partially_verified | blocked

개발 컨텍스트 요약
- <current technical shape, most important progress fact, and largest risk>

근거 범위와 최신성
- Slack: <source/channel, searched range, checked-through time, gaps>
- 문서·WBS: <versions/hashes and authority>
- 저장소·PR: <coverage count and gaps>
- AWS·Shopify: <live/configured/unavailable coverage>

저장소와 전달 상태
- <repository@inspected-SHA> — <role, fetched default SHA, branch/dirty, open PRs, checked time>
- <unavailable mapped repository> — <reason and impact>

현재 시스템 흐름
```mermaid
<verified solid edges; inferred or unverified dashed edges>
```

AWS·네트워크·IAM
- 계정·주체·리전: <observed values and time, or 미확인>
- <resource> — <configured|deployed|live|unverified, network/IAM relationship, source>
- IAM 유효 권한 제한: <trust/policy/boundary/resource-policy/SCP coverage>

AWS 배포 구조
```mermaid
<account/region/VPC/runtime/data/event/observability diagram with evidence labels>
```

Shopify·외부 연동
- <app/webhook/function/admin/theme/integration> — <declared|registered|active|observed, evidence>

개발 진행현황
- 완료: <items and acceptance/deployment evidence>
- 진행 중: <items and active evidence>
- 검수 대기: <verification_pending items and missing evidence>
- 차단: <items and blocker>
- 상태 미확인: <items and required evidence>
- 범위 기준: <authoritative denominator and X/Y, or 전체 진행률 산정 불가>

다음 착수 가능 작업
- <ready key, completed dependencies, accepted criteria, repository/start workflow>
- 착수 불가 시: <착수 가능 항목 없음 and smallest unblock action>

아키텍처 차이·위험
- <desired vs configured vs deployed vs live conflict or unknown>

DB 저장 결과
- 아키텍처 스냅샷: <version/id>
- 새 근거·이벤트: <identifiers>
- 저장 실패: <reason or 없음>
````

Use `verified` only when every material current-state node, relationship, repository, and progress claim has current direct or corroborated evidence. Use `partially_verified` when the report is useful with visible gaps. Use `blocked` when project identity or missing critical access prevents a responsible technical baseline.
