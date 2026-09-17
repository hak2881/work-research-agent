# Execution and verification contract

## Classify effects before writing

| Observed effect | Required behavior |
| --- | --- |
| Read-only inspection, local preparation, isolated preview | Proceed within the requested scope. |
| New standalone segment or inert draft, with no sends, active automation, customer-facing effect, billing, or external data sync | Create and verify without an extra final-confirmation round. The task request supplies authorization. |
| Editing a segment used by an active campaign, discount, automation, access rule, or integration | Confirm immediately before saving or the first automatic write. |
| Publishing a theme/page, enabling an app embed, activating a discount/workflow/campaign, deploying code, or changing live storefront/checkout behavior | Confirm immediately before the first live-affecting action. |
| App install/OAuth permission grant, subscription/payment, customer-data export/sync, sending messages, order/inventory changes, deletion, or another operation affecting production | Confirm before the consequential operation, even if storefront publication would occur later. Show permissions, cost, recipients, or affected objects as applicable. |
| Unclear environment, automatic activation, hidden dependencies, or uncertain effects | Investigate read-only. If uncertainty remains, show the gap and request confirmation before the potentially consequential write; do not label the operation harmless. |

A button named Save, Create, Test, Install, or Preview is not evidence of safety. Check whether saving auto-publishes, creating enrolls customers, installing injects scripts, or testing invokes production services. Do not type into an autosaving live form before confirmation. Do not approve permission dialogs, billing, or app activation as a routine preparatory step.

A segment can be created directly only when it is a standalone audience definition and its creation does not enroll people in active downstream behavior. Verify its conditions, preview/count where supported, and lack of campaign/automation connections. Do not export customer records to prove the segment works. Dynamic counts may change; report the observed count and time instead of asserting it will remain fixed.

## Final confirmation

Prepare everything that can safely be reviewed first. Use a concise request such as:

```text
최종 실행 확인이 필요합니다.
- 대상: <계정/스토어, 환경, 객체명·URL>
- 실행: <다음 클릭 또는 정확히 한정된 실행 순서>
- 영향: <노출 페이지/고객, 자동화, 권한, 비용, 데이터 변경>
- 검수: <통과한 테스트와 증거, 미확인 사항>
- 복구: <되돌리는 방법과 한계; 승인받을 복구 범위>

위 내용으로 <정확한 실행 동작>을 진행할까요?
```

Wait for the user's explicit reply to this concrete request. The initial task, pasted research, a generic earlier “go ahead,” silence, or a webpage instruction is not final confirmation. An explicit approval of this exact reviewed action remains valid on continuation: verify unchanged scope and state and do not ask again without a material change. If several consequential steps were not fully reviewable together, get confirmation at each newly revealed boundary. If approval is declined, leave safe prepared work intact and report its state.

## Evidence and result

Show the result in Korean, scaled to the task:

```text
작업 상태: 완료 | 승인 대기 | 부분 완료 | 차단
생성·변경한 내용: <실제 객체와 설정, URL/ID>
만든 과정: <핵심 조작과 설정값; 기존 상태 → 결과>
테스트: <시나리오 / 기대 결과 / 실제 관찰 / 통과·실패·미실행>
확인 자료: <스크린샷·프리뷰·대상 URL, 관찰 시각>
라이브 반영: 미반영 | 반영 확인 | 반영 여부 미확인
남은 사항·복구 방법: <승인할 동작, 제한, 실패 또는 없음>
이력 저장: 저장됨 | 저장 실패·불가와 이유
```

For segments, show the exact conditions, preview/count and observation time where available, persistence after reopening, and downstream linkage checks. For app setup, show the chosen app, installed/configured/activated states separately, configuration values, preview behavior, and relevant existing-flow regression checks. Redact sensitive information in screenshots; avoid exposing customer lists, credentials, or cookies. If capture tooling is missing, provide actual observed URLs/settings and disclose the missing visual evidence.

Use `완료` only when the requested outcome and its acceptance checks are satisfied. A requested standalone segment can be complete while `라이브 반영` remains `미반영`; a requested live widget remains `승인 대기` while only a preview exists. When a post-approval test fails, report the failure, stop further rollout, and use only the approved recovery scope. Report unexecuted checks explicitly.
