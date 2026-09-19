# Work Research Agent

`work-research-agent`는 Codex와 Claude Code에서 동작하는 플러그인입니다. 별도 에이전트 모델을 실행하지 않으며, 각 호스트에서 스킬을 실행하는 동안 해당 호스트의 모델과 토큰을 사용합니다.

Slack 문의 링크를 받으면 관련 프로젝트와 과거 의사결정을 찾고, Git 및 현재 코드, Shopify 기능이나 앱 동작을 다시 확인한 뒤 검수 가능한 한국어 PM 답변 초안을 만듭니다. 사용자가 명시적으로 요청하지 않는 한 Slack에는 게시하지 않습니다.

## 제공 기능

- `$work-history <사람>`: 최초 1회 접근 가능한 Slack 전체 과거 대화에서 관련 프로젝트를 식별하고, 프로젝트별 저장소를 클론해 실제 요청·결정·구현·검수·완료 기록을 초기 데이터로 만듭니다.
- `$work-research [1|2] <Slack 링크>`: 관련 이력과 현재 근거를 다시 검사합니다. 고객사 답변에는 요청과 검토 상태만 정리하고 구현 방식을 확정하지 않습니다. 개발자 전달문은 요청·핵심 확인 사항·넓은 후보만 한 문단으로 전달해 적절한 작업 방안을 검토하도록 요청합니다. 이어서 구현 영역(프론트엔드·백엔드·공동·개발 불필요·미확인)과 근거를 정리합니다. 코드 판단 전 원격 기본 브랜치를 최신화하며, 공수와 일정은 산정하지 않고 `$dev-plan`으로 연결합니다. `1`은 재발 방지 관점과 현재 요청 관점을 함께 제시하고 각 방안의 구현 영역을 따로 판정하며, `2`는 고객사가 요청한 내용에 집중합니다.
- `$work-prd <Slack 링크 | 프로젝트명 + 범위 | 문서>`: 관련 이력과 최신 원본을 대조하여 LUKUKU 표준 8개 섹션의 PRD를 작성합니다. 확정·확인 필요·보류를 구분하고 편집 가능한 HTML과 공유용 PDF를 생성해 버전과 근거를 DB에 연결합니다. 공수와 개발 TODO는 만들지 않으며 검토된 PRD를 `$dev-plan`으로 넘깁니다.
- `$work-status <프로젝트>`: 저장된 이력과 마지막 근거 이후의 Slack·Git 상태를 확인해 완료·진행 중·차단·미확인 현황을 보고합니다.
- `$work-act <작업 내용 또는 리서치 결과>`: 실행 가능성과 현재 상태를 재검증한 뒤 Playwright로 앱 설정·세그먼트 생성 등의 작업을 수행하고 결과와 테스트 증거를 보여줍니다. 라이브 반영이나 운영에 영향을 주는 동작은 바로 직전에 최종 확인을 받습니다.
- `$dev-plan <PRD·WBS·Slack 링크·문서>`: PM에게 전달할 답변을 먼저 작성하고 요구사항, 현재 코드, 과거 결정을 교차 검수합니다. 문서와 표 구조를 보존해 원문과 대조하고, 간단한 검토는 세션에 답변하며, 구조화가 필요한 검토만 근거 중심 HTML 보고서로 만듭니다. 개발 가능성, 공수 범위, 의존성, 완료 조건과 작업 목록도 DB에 기록합니다.
- `$dev-implement <작업 ID·Slack 링크>`: 원문과 승인된 계획을 다시 대조한 뒤 정확히 하나의 작업만 `$b-start`로 개발합니다. 결과는 기본적으로 간결하게 보고하고, 복잡한 흐름·매핑·검수 근거에만 HTML을 사용합니다. `$b-end`와 `$b-deploy`는 실행하지 않습니다.
- `$dev-context <프로젝트>`: 모든 저장소와 PR, 코드 흐름, AWS·Shopify 구조, 개발 진행현황과 다음 착수 가능 작업을 근거와 Mermaid로 정리합니다.
- `$dev-pr [작업 ID·Slack 링크]`: 인자를 생략하면 현재 저장소와 최근 구현 이력에서 방금 작업한 항목을 찾고, 검증된 대상 브랜치로 push와 PR 생성만 수행합니다.
- 로컬 SQLite + FTS5 MCP: 프로젝트, 작업 근거, 문서 버전, 개발 작업과 상태 이력, 공수, 완료 조건, 아키텍처 스냅샷, 저장소와 커밋을 검색 가능한 형태로 보관합니다.
- Codex의 기존 Slack, GitHub, Shopify, Playwright 도구를 사용하므로 조사와 답변 생성도 현재 Codex 세션에서 수행됩니다.

SQLite는 검색 인덱스이자 근거 기록입니다. 변경 가능성이 있는 사실은 답변 전에 원본 Slack 쓰레드, 최신 Git SHA, Shopify Admin 또는 브라우저에서 재검증합니다.

## Codex 설치

```bash
codex plugin marketplace add hak2881/work-research-agent
codex plugin add work-research-agent@work-research
```

설치 후 새 Codex 쓰레드를 열고 다음처럼 실행합니다.

```text
$work-history 김병학
$work-status <프로젝트>
$work-research 1 https://your-workspace.slack.com/archives/C01234567/p1234567890
$work-research 2 https://your-workspace.slack.com/archives/C01234567/p1234567890
$work-research https://your-workspace.slack.com/archives/C01234567/p1234567890  # 2와 동일
$work-prd https://your-workspace.slack.com/archives/C01234567/p1234567890
$dev-plan <PRD 또는 WBS>
$dev-context <프로젝트>
$dev-implement <작업 ID 또는 Slack 링크>
$dev-pr
```

`$work-history`는 초기 구축 때 한 번 사용합니다. 저장소는 사람 소유가 아니라 식별된 프로젝트를 기준으로 `~/projects/lukuku/<project>/<repository>`에 수집합니다. 이후에는 `$work-research`가 문의를 조사할 때 새로 확인한 근거를 해당 프로젝트 이력에 자동으로 추가합니다.

모델 선택이나 별도 AI API 키 설정은 필요하지 않습니다. Slack 계정 연결과 조사 대상 채널 접근 권한은 필요합니다. 자세한 내용은 [Codex 설치 가이드](docs/codex-installation.md)를 참고하세요.

Hermes 호환 설정도 유지하지만 선택 사항입니다. 필요한 경우에만 [Hermes 설치 가이드](docs/hermes-installation.md)를 사용하세요.

## Claude Code 설치

```bash
claude plugin marketplace add hak2881/work-research-agent
claude plugin install work-research-agent@work-research --scope user
```

Claude Code에서는 다음처럼 실행합니다.

```text
/work-research-agent:work-history 김병학
/work-research-agent:work-research 1 <Slack 링크>
/work-research-agent:work-research 2 <Slack 링크>
/work-research-agent:work-research <Slack 링크>
/work-research-agent:work-prd <Slack 링크 또는 프로젝트명 + 범위>
/work-research-agent:dev-plan <PRD 또는 WBS>
/work-research-agent:dev-context <프로젝트>
/work-research-agent:dev-implement <작업 ID 또는 Slack 링크>
/work-research-agent:dev-pr
```

자세한 내용은 [Claude Code 설치 가이드](docs/claude-code-installation.md)를 참고하세요.

## 답변 형식

코드 수정이나 개발자 확인이 필요한 경우에는 두 답변을 분리합니다.

```text
개발자에게 요청할 내용
개발자: 현재 코드 기준으로 <구현 방향>으로 개발할 수 있을 것으로 보입니다. <확인할 사항> 검수 부탁드립니다.

고객사에게 답변할 내용
PM: 문의해 주신 내용은 개발 확인이 필요한 사항입니다. 내부 검토 후 다시 안내드리겠습니다.
```

개발자 확인이 필요 없는 문의는 선택한 조사 모드에 맞춰 답변합니다. 모드 `1`은 `A. 재발 방지 관점`과 `B. 현재 요청 관점`을 함께 보여주며, 근본 원인은 현재 문의를 직접 재현하거나 코드 흐름 끝까지 추적한 경우에만 확정합니다. 모드 `2`와 번호를 생략한 호출은 고객사가 요청한 내용에 집중합니다.

```text
PM: <검수 후 보낼 수 있는 답변>

확인 근거
- <사실과 출처>

확실하지 않은 부분
- <부족한 접근 권한, 충돌, 가정 또는 없음>

검수 상태: verified | partially verified | blocked
확인한 코드: <repository>@<SHA> | 해당 없음

답변 복사
재검수 <부분>
전체 재검수
```

모드 `1`에서는 `복사 A` 또는 `복사 B`로 원하는 PM 답변 본문을 선택합니다. `재검수 <부분>`은 지정한 근거를 새로 수집하고, `전체 재검수`는 프로젝트 판별부터 독립적으로 다시 확인합니다.

## 조사 이후 실제 작업

리서치 결과나 원하는 작업을 `$work-act` 뒤에 붙여 넣습니다. Slack 링크 없이 직접 작업을 요청할 수도 있습니다.

```text
$work-act <스토어 URL>에서 최근 90일 구매 고객 세그먼트를 만들어 주세요. 캠페인에는 연결하지 마세요.
$work-act <리서치 결과>에 따라 앱 설정을 준비하고 프리뷰에서 검수해 주세요. 라이브 적용 직전에 확인받아 주세요.
```

Claude Code에서는 `/work-research-agent:work-act <작업 내용>`으로 실행합니다. 실제 브라우저 작업에는 Playwright 도구와 대상 서비스 로그인·권한이 필요합니다.

독립 세그먼트나 운영 영향이 없는 초안은 요청 범위에서 생성하고 다시 열어 저장 상태를 검증합니다. 활성 캠페인·자동화에 영향을 주는 세그먼트 수정, 앱 설치·권한 허용·과금, 고객 데이터 동기화, 테마 게시·앱 활성화 등은 정확한 대상·변경·영향·테스트·복구 방법을 먼저 보여주고 최종 승인을 기다립니다. 자동 저장으로 라이브에 반영되는 화면은 입력 전부터 이 경계를 적용합니다.

결과에는 생성한 객체 링크와 설정, 만든 과정, 테스트별 기대/실제 결과, 가능한 스크린샷·프리뷰, 라이브 반영 여부, 이력 저장 여부를 표시합니다. 새 실행·검수 근거도 기존 프로젝트 이력에 축적합니다. 이 승인 절차는 호스트 모델이 따르는 스킬 지침이며, Python MCP가 브라우저 클릭을 기술적으로 차단하는 장치는 아닙니다.

## 로컬 데이터

기본 DB 위치:

```text
~/.local/share/work-research-agent/history.sqlite3
```

Git 체크아웃 기본 위치:

```text
~/projects/lukuku/<project>/<repository>
```

인증 토큰, 브라우저 쿠키, Slack·Shopify 자격 증명은 저장소나 SQLite에 저장하지 않습니다. 스키마는 [docs/schema.md](docs/schema.md)에 설명되어 있습니다.

## 개발

```bash
uv sync --dev
uv run pytest -q
uv run python scripts/validate_distribution.py
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/work-research-agent
```

MCP 서버를 직접 실행하려면:

```bash
WORK_RESEARCH_DB=/tmp/work-history.sqlite3 uv run work-research-history
```

## 한계

- 연결된 Slack 계정이 읽을 수 있는 채널만 검색할 수 있습니다.
- Git 커밋은 코드 변경의 근거이며 배포 또는 고객 승인까지 증명하지는 않습니다.
- 프로젝트와 저장소 연결이 불명확하면 추측하지 않고 검토 대상으로 표시합니다.

## License

MIT
