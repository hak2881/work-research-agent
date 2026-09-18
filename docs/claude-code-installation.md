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
/work-research-agent:work-research https://your-workspace.slack.com/archives/C01234567/p1234567890
/work-research-agent:work-act <작업 내용 또는 리서치 결과>
/work-research-agent:dev-plan <PRD·WBS·Slack 링크·문서>
/work-research-agent:dev-context <프로젝트>
/work-research-agent:dev-implement <작업 ID>
```

`work-history`는 최초 초기 데이터 구축에 한 번 사용합니다. Slack 이력에서 관련 프로젝트를 판별하고, 사람의 소유 저장소가 아니라 프로젝트별 관련 저장소를 `~/projects/lukuku/<project>/<repository>`에 수집합니다.

`work-act`는 Playwright로 현재 상태를 확인하고 작업·검수합니다. 운영 영향이 없는 독립 세그먼트·초안은 생성할 수 있으며, 라이브 반영이나 운영에 영향을 주는 실행 직전에 최종 승인을 요청합니다. Playwright 연결과 대상 서비스 로그인·권한이 필요하며, 결과에는 생성 내용·과정·테스트 증거·라이브 반영 여부가 포함됩니다.

## 데이터

Codex와 Claude Code의 기본 로컬 DB 경로는 같습니다.

```text
~/.local/share/work-research-agent/history.sqlite3
```

Claude Code에 별도로 Slack 연결 권한이 있어야 Slack 원문을 검색할 수 있습니다. 플러그인 설치만으로 Codex의 Slack 인증이 Claude Code에 복사되지는 않습니다.
