# Work Research Agent

`work-research-agent`는 현재 사용 중인 Codex 안에서 동작하는 Codex plugin입니다. 별도 에이전트 모델이나 API 키를 요구하지 않으며, `/work-history`와 `/work-research`를 실행하는 동안 **Codex의 모델과 토큰**을 그대로 사용합니다.

Slack 문의 링크를 받으면 관련 프로젝트와 과거 의사결정을 찾고, Git 및 현재 코드, Shopify 기능이나 앱 동작을 다시 확인한 뒤 검수 가능한 한국어 PM 답변 초안을 만듭니다. 사용자가 명시적으로 요청하지 않는 한 Slack에는 게시하지 않습니다.

## 제공 기능

- `/work-history <사람 또는 프로젝트>`: 접근 가능한 Slack 대화와 Git 저장소에서 근거, 결정, TODO, 저장소 및 커밋 이력을 수집합니다.
- `/work-research <Slack 링크>`: 해당 문의와 실제로 연관된 이력만 선별하고 코드, Shopify, 공식 문서, 브라우저 증거를 다시 검사합니다.
- 로컬 SQLite + FTS5 MCP: 프로젝트, 근거, TODO, 저장소, 커밋과 출처 관계를 검색 가능한 형태로 보관합니다.
- Codex의 기존 Slack, GitHub, Shopify, Playwright 도구를 사용하므로 조사와 답변 생성도 현재 Codex 세션에서 수행됩니다.

SQLite는 검색 인덱스이자 근거 기록입니다. 변경 가능성이 있는 사실은 답변 전에 원본 Slack 쓰레드, 최신 Git SHA, Shopify Admin 또는 브라우저에서 재검증합니다.

## Codex 설치

```bash
codex plugin marketplace add hak2881/work-research-agent
codex plugin add work-research-agent@work-research
```

설치 후 새 Codex 쓰레드를 열고 다음처럼 실행합니다.

```text
/work-history 김병학
/work-research https://your-workspace.slack.com/archives/C01234567/p1234567890
```

모델 선택이나 별도 AI API 키 설정은 필요하지 않습니다. Slack 계정 연결과 조사 대상 채널 접근 권한은 필요합니다. 자세한 내용은 [Codex 설치 가이드](docs/codex-installation.md)를 참고하세요.

Hermes 호환 설정도 유지하지만 선택 사항입니다. 필요한 경우에만 [Hermes 설치 가이드](docs/hermes-installation.md)를 사용하세요.

## 답변 형식

```text
PM: <검수 후 보낼 수 있는 답변>

확인 근거
- <사실과 출처>

확실하지 않은 부분
- <부족한 접근 권한, 충돌, 가정 또는 없음>

검수 상태: verified | partially verified | blocked
확인한 코드: <repository>@<SHA> | 해당 없음

1. 답변 복사
2. <부분> 재검수
3. 전체 독립 재검수
```

`1`은 PM 답변 본문만 복사하고, `2`는 지정한 부분의 근거를 새로 수집하며, `3`은 프로젝트 판별부터 독립적으로 다시 검수합니다.

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
