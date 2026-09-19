# Claude Code 설치 가이드

Claude Code에서도 Codex와 같은 스킬과 로컬 SQLite MCP를 사용할 수 있습니다. 두 호스트의 기본 DB 경로가 같으므로 같은 사용자 계정에서 실행하면 작업 이력을 공유합니다.

## 설치

터미널에서 실행합니다.

```bash
claude plugin marketplace add hak2881/work-research-agent
claude plugin install work-research-agent@work-research --scope user
```

실행 중인 Claude Code 세션에서는 다음 명령으로 다시 불러옵니다.

```text
/reload-plugins
```

## 사용

Claude Code 플러그인 스킬은 플러그인 이름이 붙습니다.

```text
/work-research-agent:work-history 김병학
/work-research-agent:work-status <프로젝트>
/work-research-agent:work-research 1 https://your-workspace.slack.com/archives/C01234567/p1234567890
/work-research-agent:work-research 2 https://your-workspace.slack.com/archives/C01234567/p1234567890
/work-research-agent:work-research https://your-workspace.slack.com/archives/C01234567/p1234567890
/work-research-agent:work-act <작업 내용 또는 리서치 결과>
/work-research-agent:dev-plan <PRD·WBS·Slack 링크·문서>
/work-research-agent:dev-context <프로젝트>
/work-research-agent:dev-implement <작업 ID 또는 Slack 링크>
/work-research-agent:dev-pr [작업 ID 또는 Slack 링크]
```

`work-research 1`은 재발 방지 관점과 현재 요청 관점의 답변을 함께 만듭니다. `work-research 2`는 고객사가 요청한 내용에 집중하며, 번호를 생략해도 `2`로 동작합니다. 근본 원인은 현재 문의에서 직접 재현하거나 코드 흐름을 끝까지 추적한 경우에만 확정합니다.

`work-history`는 최초 초기 데이터 구축에 한 번 사용합니다. Slack 이력에서 관련 프로젝트를 판별하고, 사람의 소유 저장소가 아니라 프로젝트별 관련 저장소를 `~/projects/lukuku/<project>/<repository>`에 수집합니다.

`work-research`에서 개발자 확인이 필요하면 검증된 사실과 권장 방안을 분리하고 구현 가능성과 더 나은 대안을 검수 요청합니다. 근거가 부족하면 방안을 추측하지 않습니다. 공수와 일정 산정은 하지 않고 `$dev-plan`으로 연결합니다.

조사 결과는 고객사 답변을 먼저 표시하고, 답을 바꾸는 핵심 판단과 꼭 필요한 개발자 검수 항목만 이어서 보여줍니다. 정상적인 Git·도구·이력 저장 로그는 결과에서 생략합니다.

`work-research`에서 코드 검수가 필요하면 원격 기본 브랜치를 먼저 `fetch`합니다. 깨끗한 기본 브랜치는 fast-forward 방식으로 최신화하고, 다른 브랜치나 로컬 변경이 있으면 최신 원격 SHA를 임시 worktree에서 검수하여 기존 작업을 보존합니다.

`dev-plan`은 PM에게 전달할 답변을 먼저 작성합니다. 간단한 검토는 세션에 답변하고, 비교표·다이어그램·복수 대안이나 긴 근거가 필요한 검토는 `~/.local/share/work-research-agent/reports/`에 상세 HTML 보고서를 생성합니다. 답변을 Slack에 자동 게시하지는 않습니다.

`dev-plan`과 `dev-implement`는 문서와 표의 구조를 보존해 원문과 렌더링 결과를 대조하고, 결론과 근거가 명확해지는 범위에서만 HTML을 사용합니다. 구현 시에는 생성된 보고서보다 승인된 원문과 현재 코드가 우선합니다.

`work-act`는 Playwright로 현재 상태를 확인하고 작업·검수합니다. 운영 영향이 없는 독립 세그먼트·초안은 생성할 수 있으며, 라이브 반영이나 운영에 영향을 주는 실행 직전에 최종 승인을 요청합니다. Playwright 연결과 대상 서비스 로그인·권한이 필요하며, 결과에는 생성 내용·과정·테스트 증거·라이브 반영 여부가 포함됩니다.

## 데이터

Codex와 Claude Code의 기본 로컬 DB 경로는 같습니다.

```text
~/.local/share/work-research-agent/history.sqlite3
```

Claude Code에 별도로 Slack 연결 권한이 있어야 Slack 원문을 검색할 수 있습니다. 플러그인 설치만으로 Codex의 Slack 인증이 Claude Code에 복사되지는 않습니다.
