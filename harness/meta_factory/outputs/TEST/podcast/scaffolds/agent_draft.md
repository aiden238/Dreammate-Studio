# agent_draft.md — palette: critic agent scaffold (팟캐스트)

> 위치: `harness/meta_factory/outputs/TEST/podcast/scaffolds/agent_draft.md`
> 기반: `meta_factory/templates/agent_template.md`
> 상태: Phase M1 S1 dry-run scaffold (active 아님, 설계 문서 — 런타임 코드 0줄, A9)
> 대상 예시: `critic` agent (1개 — template 자리표시자 채움 예시)

---

## 채운 scaffold (agent_template placeholder → 팟캐스트)

```yaml
# ── agent: critic ──────────────────────────────────────────
name: critic
responsibility: "에피소드 기획안 평가 (canonical overall_score + dimensions: 후킹/대화흐름/질문품질)"
inputs:                              # envelope 필드 / 이전 agent 출력
  - episode_plan_dict                # planning(또는 rewriter) 출력 1개
  - question_list                    # (게스트 모드) question agent 출력 — 선택
  - shownotes                        # shownotes agent 출력 — 선택
outputs:                             # output_schema 필드
  - overall_verdict                  # accept | revise
  - overall_score                    # canonical (0~1 또는 0~10 — output_schema 정의 따름)
  - dimensions                       # opening_hook_strength / conversation_flow / question_quality ...
forbidden_actions:                   # ★ 필수 — 격리
  - 기획안 직접 수정 (rewriter 가 담당)
  - 다른 agent 직접 호출 (supervisor 패턴 — orchestrator 경유)
  - 오디오/TTS 산출 (forbidden_scope)
prompt_ids:                          # prompt_registry 식별자 (placeholder)
  - P-PODCAST-CRITIC-001
execution_policy:
  timeout_ms: 30000                  # 시간 초과 → silent fail 금지 (에러 응답 + 부분 결과)
  max_retries: 2
  graceful_on_failure: true          # critic 실패 시 graceful skip → 기획안 생성 차단 X
```

---

## 작성 가이드 점검 (agent_template §작성가이드)

1. ✅ forbidden_actions 필수 — supervisor 패턴 → "다른 agent 직접 호출 금지 (orchestrator 경유)" 명시.
2. ✅ inputs/outputs 는 agent_io_contract / output_schema 와 정합 예정 (episode_plan_dict / overall_verdict / dimensions).
3. ✅ idempotent — 같은 episode_plan_dict → 같은 평가 (캐시 가능).
4. ✅ graceful 실패 — critic 실패 시 차단 0 + validation.warnings 자기설명.
5. (해당) producer_reviewer 조합 — revise 상한은 rewriter 측 critic_max_revise=2 에서 차단.
6. ★ 런타임 0 — 본 scaffold 는 설계만. 실제 critic.py 는 사용자 승인 후 별도 phase.

## Dreammate 대비 차이 (관찰)

- Dreammate critic dimensions = 8(영상). 팟캐스트 critic = hook→opening_hook_strength, structure→conversation_flow, +question_quality/guest_fit(조건부). 조건부 차원 입력(question_list/shownotes 선택)은 agent_template 에 conditional 슬롯이 없어 inputs 주석으로 표기 (GAP G3/G4).
