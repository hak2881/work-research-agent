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

`/work-history`가 Slack 전체 이력을 찾으려면 Codex에 연결된 Slack 계정이 대상 공개 채널과 비공개 채널의 멤버여야 합니다. 계정을 바꾼 뒤에는 새 쓰레드에서 접근 여부를 다시 검사합니다.

Shopify 문의는 종류에 따라 다음 근거를 사용합니다.

- 현재 코드 또는 Shopify Function 문의: 저장소를 동기화하고 정확한 SHA에서 코드를 확인
- Shopify Admin 기능 문의: Admin API 또는 실제 Admin 화면에서 확인
- 앱 설치·설정 흐름 문의: Playwright로 앱 페이지와 가능한 설정 흐름을 직접 확인
- 정책이나 플랫폼 제한 문의: 최신 Shopify 공식 문서 확인

## 사용

처음 설치한 뒤 사람의 전체 과거 작업 이력을 한 번 구축합니다.

```text
/work-history 김병학
```

이 초기 구축은 보통 한 번만 실행합니다. 이후 Slack 링크 하나로 문의를 조사합니다.

```text
/work-research https://your-workspace.slack.com/archives/C01234567/p1234567890
```

`/work-research`는 조사 과정에서 새로 검증한 요청, 결정, 구현과 결과를 로컬 이력에 자동으로 추가합니다. 초기 구축이 빠졌다면 해당 문의에 필요한 프로젝트와 기간만 보충하며, 사람 전체 이력을 다시 수집하지 않습니다.

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
- 답변이 `partially verified`이면 `2 <부분>` 또는 `3`을 선택해 근거를 새로 수집할 수 있습니다.
