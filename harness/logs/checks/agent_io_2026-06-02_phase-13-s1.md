# agent-io-check 결과 — Phase 13 S1 (output_schema §8.1 v1.2.0, CC-012)

- 일자: 2026-06-02
- 트리거: `docs/contracts/output_schema.md` §8.1 변경 (Plan rich 슬롯 12종 additive) 후 영향 agent 정합 검증
- 대상 agent: **Planner (P-006)** — 한 번에 한 agent (Critic/Rewriter 소비 회귀는 §부수 확인)
- 판정: **PASS (발견 0건 — 정합)**

## 컨트랙트 로드
- `agent_io_contract.md §4` Planning — **Input §4.2 무변경**, **Output §4.3 = "output_schema.md §8 P-006 body" 참조** (필드 미중복 → 본문 변경 불필요).
- `output_schema.md §8.1` = **v1.1.0 → v1.2.0** (Plan rich 9 + PlanFlowBeat rich 3, 전부 Optional).
- 구현/prompt: `agents/planning.py` SYSTEM_PROMPT (compact 7필드 산출) + `schemas/output.py` Plan/PlanFlowBeat (rich Optional 추가).

## 차이 식별 (Planner P-006)

```
대상 agent : Planner (P-006)
contract   : agent_io_contract.md §4.3 → output_schema.md §8.1 v1.2.0
구현/prompt: planning.py SYSTEM_PROMPT (compact) + schemas/output.py Plan

match      : 11 필드  (compact 7: name/concept/hook/flow/pros/risks/approach_label
                       + flow beat 4: beat_index/beat/duration_sec/purpose)  — 구현↔contract↔모델 일치
extra      : 0 필드  (구현이 contract 에 없는 키 산출 없음)
missing    : 12 필드 (BY-DESIGN) — contract/모델에 rich 12종 존재, 현 planning prompt 는 미산출.
                      ★ 결함 아님 — 전부 Optional + gated 단계 롤아웃: rich 프롬프트=S2, 채움 분기=S3.
type_diff  : 0 필드
```

## 판단
- **rich 12 "missing" = 의도된 단계 롤아웃** (contract/모델이 먼저 슬롯 정의 = S1, prompt 채움 = S2,
  flag 분기 = S3). Optional 이므로 미산출 시에도 §8.1 valid → contract↔구현 불일치 아님.
- **agent_io_contract §4.3 변경 불요** — output 을 §8 참조로만 정의 (CC-012 가 §8.1 갱신으로 자동 반영).
- **type_diff / extra 0** — 런타임 위험 없음.

## 부수 확인 (소비자 회귀 0)
- **Critic (P-007)**: plan dict 의 기존 필드로 채점. rich 키 추가(값 None/[])는 미참조 → 회귀 0. (depth_actionability 차원 = S4)
- **Rewriter (P-008)**: orchestrator(`moa_orchestrator.py` L319)가 named 7필드로 Plan 재구성 → rich 기본값 유지 → 회귀 0.
- **Orchestrator**: `Plan(...)` 생성(L205/L319)이 named 7필드만 전달 → rich 미채움(기본값). model_dump 출력에 rich 키만 None/[] 로 추가(기존 7필드 값 불변).
- **회귀 테스트**: `pytest backend/fastapi/tests` = **481 passed** (기존 471 + 신규 10, 기존 수정 0).

## 후속
- contract 변경: 불요 (§4.3 참조 구조 — CC-012 §8.1 갱신으로 충분).
- prompt 변경(rich 산출): **S2** — prompt-version-review (P-006 v1.0.0 → v1.1.0).
- gated 분기(OFF=compact byte-identical via `Plan.model_dump_compact()`): **S3**.
