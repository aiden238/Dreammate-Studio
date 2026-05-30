# moa_policy.md — MOA Lite Policy

> 위치: `ai_system/orchestration/moa_policy.md`
> 상태: S4-3 deep
> 참조: `ai_system/orchestration/flow.md`, `ai_system/orchestration/fallback_policy.md`, `cost_control_policy.md`
> 참조: `docs/contracts/agent_io_contract.md`
> 명명: 모든 agent는 Intent / Planning / Critic / Rewriter (MOA Lite 표준)

---

## 1. 정의

**MOA = Mixture of Agents**. 여러 agent가 협력해 단일 결과를 생성하는 패턴.

**MOA Lite**는 MVP용 경량 버전으로 다음 제약을 둔다:
- agent 수 4개로 고정 (Intent / Planning / Critic / Rewriter)
- 동기 처리 (Phase 0~10)
- 추가로 P-AUX-1 (intent_filter), P-AUX-2 (memory_extractor)를 보조 prompt로 운영
- Recursive MOA 금지 (revise_round 2 한도)
- LangGraph 등 외부 그래프 프레임워크 미사용

---

## 2. 4 Agent 협력 모델

```
Intent      → 의도 분류 + Discovery/Quick 분기 + 카드 5장 생성 (1~5회 호출/세션)
Planning    → 3 plan_candidates 생성 (1회 호출/세션)
Critic      → 8 차원 채점 × 3 plan 병렬 (3회 호출/세션, 재평가 시 +0~6회)
Rewriter    → revise 판정 시 개선 (0~3회 호출/세션, 사용자 트리거)
```

요청당 LLM 호출 수 목표: **5~10회/세션** (cost_saving 모드는 3~5회).

agent 간 직접 호출 금지. 오케스트레이터(backend service layer)가 항상 중개한다 (agent_io §1).

> **실 구현 (Phase 8 ADR-027)**: `backend/fastapi/orchestration/moa_orchestrator.py::generate_plan()`
> 이 4 agent 중개를 담당한다 (Intent → RAG → 3-plan(Planning) → Critic(+revise loop) → save → Envelope).
> 기존 routers/plans.py 의 god-function 을 behavior-preserving 추출 (Envelope byte-identical, pytest 회귀 0).
> 진행 상황은 `orchestration/progress_sink.py::ProgressSink` 로 stage 단위 emit (NullProgressSink default,
> StoreProgressSink → SSE 브릿지 ADR-028). agent_io_contract §8 정합.

---

## 3. 데이터 전달 (envelope 유지)

모든 agent 입력은 공통 envelope(agent_io §2)로 wrapping된다:

```
{
  "request": { request_id, user_id, session_id, video_id, trace_id, issued_at },
  "agent": "intent | planning | critic | rewriter | memory_extractor",
  "prompt_id": "P-XXX",
  "prompt_version": "v1.0.0",
  "input": { /* agent별 body */ },
  "execution": { model, timeout_ms, max_retries, temperature, max_tokens, stream }
}
```

agent 간 데이터 전달 시 envelope는 새로 생성하고, body의 필요한 필드만 복사 (다음 단계 input schema 준수).

---

## 4. 비동기 vs 동기 선택

| Phase | 모드 | 이유 |
|---|---|---|
| 0~10 | **동기** (현재) | 사용자가 30~60초 안에 결과 받는 UX. SSE로 진행 상황 노출. |
| 11+ | 비동기 검토 | 트래픽 증가 + 사용자 수 증가 시 큐 기반 백그라운드 처리 |
| 21+ | 자동 비동기 | Custom RAG, Multi-agent voting 등 무거운 처리 |

Memory Extractor(P-AUX-2)만 Phase 0부터 비동기(백그라운드 큐) 운영.

---

## 5. 실패 격리 (한 agent 실패 시 폴백)

```
Intent 실패        → 사용자에게 "다시 입력해주세요" (입력 보존)
Planning 실패      → 1회 재시도 → 캐시된 generic 템플릿 → 에러 노출
Critic 1개 실패    → 나머지 2개는 진행, 실패한 1개는 verdict 없이 노출
Critic 전체 실패   → 자동 approve 가정 + "AI 검토 실패" 안내
Rewriter 실패      → 원본 plan 유지 + 수동 수정 권장
Memory Extractor 실패 → 사용자 무관, 24h 후 재시도 큐
```

→ 자세한 폴백은 `fallback_policy.md` 참조.

---

## 6. agent 추가/교체 정책

새 agent 도입 시 절차:
1. `contract-change` Skill로 agent_io_contract.md에 §추가
2. prompt_registry에 신규 P-ID + semver
3. `ai_system/agents/<agent>.md` 작성 (이 파일들과 동일 구조)
4. `dependency_map.yaml` 추가
5. golden_set 회귀 평가
6. flow.md 단계 추가

Phase 0~10에서는 새 agent 추가 보류. 11+ 검토.

---

## 7. agent 간 컨텍스트 격리

각 agent는 자신에게 명시된 입력 필드 외 다른 정보 접근 금지:

| Agent | brand_memory 필드 | RAG 접근 | DB 직접 |
|---|---|---|---|
| Intent | partial (P-002+ 부터 avoid+tone) | no | no (로그만 INSERT) |
| Planning | full | yes (approved_knowledge) | no |
| Critic | partial (avoid+tone) | no | no |
| Rewriter | full | no | no |
| Memory Extractor | full (현재 상태 읽기) | no | INSERT brand_memory_entries (조건부) |

agent_io §12, §13와 일치.

---

## 8. cost 통제와 연동

세션당 LLM 호출 누적이 다음 임계를 넘으면 cost_saving 모드 전환:
- 세션 누적 $0.020 → cost_saving
- 일일 사용자당 $0.10 → 다음날까지 차단

→ `cost_control_policy.md` 참조.

---

## 9. 의존성

- `flow.md` — 흐름 정의
- `fallback_policy.md` — 실패 처리
- `cost_control_policy.md` — 비용 한도
- `docs/contracts/agent_io_contract.md` — agent별 IO
- `ai_system/agents/*.md` — agent별 상세

---

## 10. Open Questions

1. Phase 11+ 비동기 전환 시점의 트래픽 임계(현재 미정).
2. Critic 3 모델 multi-voting 도입 시점(현재 단일 모델).
3. agent 간 직접 호출 허용 여부(현재 금지) — Phase 21+ 보안 검토.
4. Recursive MOA(revise_round 2 → 3 확장) 도입 ROI 검증 필요.
5. agent 추가 시 시간(현재 미정) — 5개 이상으로 늘면 MOA Heavy 전환 검토.
