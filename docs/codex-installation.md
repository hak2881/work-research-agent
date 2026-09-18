# Codex 설치 가이드

이 플러그인은 별도 Hermes 프로세스나 별도 모델을 실행하지 않습니다. 스킬의 판단, Slack·코드 조사, Playwright 검수와 답변 작성에는 현재 Codex 세션의 모델과 토큰이 사용됩니다. 함께 설치되는 로컬 MCP는 SQLite 읽기와 쓰기만 담당합니다.

## 요구 사항

- Codex CLI와 Codex 앱
- Python 3.11 이상
- [`uv`](https://docs.astral.sh/uv/)
- Git 및 GitHub 저장소 검색에 사용할 인증된 `gh` CLI
- 조사 대상 채널을 읽을 수 있는 Slack 연결
- Shopify 검수가 필요할 경우 Shopify 접근 권한과 브라우저 자동화 도구

## 설치

공개 GitHub marketplace를 추가하고 플러그인을 설치합니다.

```bash
codex plugin marketplace add hak2881/work-research-agent
codex plugin add work-research-agent@work-research
```

설치 여부를 확인합니다.

```bash
codex plugin list | grep work-research-agent
codex mcp list | grep work_history
```

스킬과 MCP 도구 목록은 새 쓰레드를 시작할 때 로드됩니다. 설치 직후에는 Codex 앱에서 새 쓰레드를 여세요.

## 연결 확인

`$work-history`가 Slack 전체 이력을 찾으려면 Codex에 연결된 Slack 계정이 대상 공개 채널과 비공개 채널의 멤버여야 합니다. 계정을 바꾼 뒤에는 새 쓰레드에서 접근 여부를 다시 검사합니다.

Shopify 문의는 종류에 따라 다음 근거를 사용합니다.

- 현재 코드 또는 Shopify Function 문의: 저장소를 동기화하고 정확한 SHA에서 코드를 확인
- Shopify Admin 기능 문의: Admin API 또는 실제 Admin 화면에서 확인
- 앱 설치·설정 흐름 문의: Playwright로 앱 페이지와 가능한 설정 흐름을 직접 확인
- 정책이나 플랫폼 제한 문의: 최신 Shopify 공식 문서 확인

## 사용

처음 설치한 뒤 사람의 전체 과거 작업 이력을 한 번 구축합니다.

```text
$work-history 김병학
```

이 초기 구축은 보통 한 번만 실행합니다. 이후 Slack 링크 하나로 문의를 조사합니다.

프로젝트의 현재 진행현황은 다음처럼 조회합니다.

```text
$work-status <프로젝트>
```

이 명령은 전체 이력을 다시 수집하지 않고 DB의 프로젝트 이력과 마지막 근거 이후의 Slack·Git 상태만 갱신합니다. 완료 범위가 정의된 PRD나 체크리스트가 없으면 임의 진행률을 만들지 않습니다.

```text
$work-research 1 https://your-workspace.slack.com/archives/C01234567/p1234567890
$work-research 2 https://your-workspace.slack.com/archives/C01234567/p1234567890
$work-research https://your-workspace.slack.com/archives/C01234567/p1234567890
```

`1`은 재발 방지 관점과 현재 요청 관점의 답변을 함께 만듭니다. 근본 원인은 현재 문의에서 직접 재현하거나 코드 흐름을 끝까지 추적한 경우에만 확정합니다. `2`는 고객사가 요청한 내용에 집중하며, 번호를 생략해도 `2`로 동작합니다.

`$work-history`는 사람의 저장소를 찾는 명령이 아닙니다. Slack 이력에서 관련 프로젝트를 먼저 식별한 뒤, 각 프로젝트에 속한 저장소를 `~/projects/lukuku/<project>/<repository>`에 클론합니다. 사람의 커밋은 프로젝트 작업을 연결하는 근거로만 사용합니다.

`$work-research`는 조사 과정에서 새로 검증한 요청, 결정, 구현과 결과를 로컬 이력에 자동으로 추가합니다. 초기 구축이 빠졌다면 해당 문의에 필요한 프로젝트와 기간만 보충하며, 사람 전체 이력을 다시 수집하지 않습니다.

코드 검수가 필요하면 관련 저장소에서 원격 기본 브랜치를 먼저 `fetch`합니다. 깨끗한 기본 브랜치는 fast-forward 방식으로 최신화하고, 다른 브랜치나 로컬 변경이 있으면 이를 보존한 채 최신 원격 SHA를 임시 worktree에서 확인합니다. 답변에는 실제로 검수한 SHA를 표시합니다.

## 조사 결과 실행

```text
$work-act <작업 내용 또는 리서치 결과>
```

개발 계획과 착수에는 다음 명령을 사용합니다.

```text
$dev-plan <PRD·WBS·Slack 링크·문서>
$dev-context <프로젝트>
$dev-implement <작업 ID 또는 Slack 링크>
$dev-pr [작업 ID 또는 Slack 링크]
```

`dev-implement`에 Slack 링크를 주면 전체 스레드에서 프로젝트와 기존 작업을 찾습니다. 정확한 작업이 없으면 `dev-plan` 규칙으로 작업을 만들고, 중복 작업·PR과 미해결 완료 조건이 없으며 하나의 `ready` 작업으로 확정될 때만 개발합니다. 백엔드에서는 `$b-start`까지만 사용하며 `$b-end`, `$b-deploy`, PR 병합과 배포는 실행하지 않습니다.

`dev-plan`은 PM 검토 요청의 회신 초안을 첫 번째로 제공합니다. 결론과 질문이 짧게 전달되는 검토는 세션에 작성하고, 비교표·다이어그램·복수 대안이나 긴 근거가 필요한 검토는 `~/.local/share/work-research-agent/reports/`에 상세 HTML 보고서를 생성합니다. Slack에는 자동으로 게시하지 않습니다.

`dev-plan`과 `dev-implement`는 HTML·PDF·스프레드시트의 제목, 표, 병합 헤더, 행 그룹과 각주 구조를 보존해 읽고 렌더링 결과와 대조합니다. 보고서는 결론과 근거를 먼저 보여주며, 요청에 필요하지 않은 표·다이어그램·섹션을 형식상 추가하지 않습니다. 구현 단계에서는 생성 보고서를 원본 요구사항으로 취급하지 않고 승인된 원문과 현재 코드를 다시 검수합니다.

`dev-pr`은 인자 없이 실행하면 현재 Git 저장소와 최근 구현 이력을 대조해 방금 검수한 작업을 찾습니다. 대상 브랜치가 근거로 확인되고 작업 상태가 `verification_pending`일 때만 일반 push와 PR 생성까지 수행하며 병합과 배포는 하지 않습니다.

Playwright 연결과 대상 계정의 작업 권한이 필요합니다. 현재 상태를 재확인하고 안전한 초안·독립 세그먼트를 준비·검수합니다. 라이브 반영, 앱 설치 권한·과금, 운영 자동화 등에 영향을 주는 동작 직전에는 검수 결과와 정확한 실행 내용을 보여주고 최종 확인을 받습니다. 생성한 객체·설정·테스트 결과·가능한 화면 증거와 이력 저장 여부를 보고합니다.

## 데이터 위치와 삭제

기본 DB는 다음 위치에 저장됩니다.

```text
~/.local/share/work-research-agent/history.sqlite3
```

이 파일을 백업하면 수집한 프로젝트 작업 이력, 결정 근거와 명시적인 미완료 항목을 유지할 수 있습니다. 삭제하면 다음 실행에서 빈 DB로 다시 시작합니다. 원문 코드와 저장소 파일 자체는 DB에 복사하지 않습니다.

## 업데이트

```bash
codex plugin marketplace upgrade work-research
codex plugin add work-research-agent@work-research
```

업데이트 후 새 Codex 쓰레드를 열어 갱신된 스킬과 MCP 설정을 사용합니다.

## 문제 해결

- `work_history`가 보이지 않으면 `uv --version`과 `codex mcp list`를 확인하고 새 쓰레드를 여세요.
- Slack 링크를 읽지 못하면 Codex에 연결된 Slack 계정과 채널 멤버십을 확인하세요.
- 비공개 채널은 연결 계정이 실제 멤버여야 하며, 검색 결과만으로 원문 접근을 대신할 수 없습니다.
- 답변이 `partially verified`이면 `재검수 <부분>` 또는 `전체 재검수`로 근거를 새로 수집할 수 있습니다.
