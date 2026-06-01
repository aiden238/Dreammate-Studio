# Contract Change Log — Phase 12 Slice 1 eval 측정 기반 정비 (golden_set 확대 + depth 차원)

> ID: CC-011
> Status: **decided + applied** (2026-06-02, Phase 12 Slice 1)
> Date: 2026-06-02
> Decision: Phase 12 검증의 측정 기반 정비 — golden_set 15 → 25 확대 (도메인 다양성↑) + "기획 깊이·실행가능성(depth_actionability)" 평가 차원 추가 (rubric, real/human 전용)
> Author: Claude (Phase 12 Slice 1 sub-agent)
> Related contracts: `eval/golden_set.md` (회귀 단일 출처), `eval/video_planning_eval.md` (평가 차원 정의), `eval/human_review_rubric.md` (사람 채점 rubric)
> Related ADR: ADR-033 (`docs/decisions/phase_9_5_eval_run_harness.md` — mock primary + 실 LLM mode flag)
> Related CC: CC-009 (`2026-05-31_phase-10-eval.md` — golden_set 11→15 + rag_eval_rubric)
> Skill: contract-change (절차) + eval-design (golden_set 확대 + 신규 차원)

---

## 1. 변경 요약

| 대상 | 변경 | 종류 |
|---|---|---|
| `eval/golden_set.md` | 15 → 25 케이스 (GS-001~015 보존 + GS-016~025 추가). §0 케이스 수 / §2 헤더 / §2.16~2.25 케이스 블록 / §3 우선순위 (P0 8 / P1 12 / P2 5) / §7 cross-ref 표 / §9 v1.2.0 entry. | **additive** (기존 케이스·우선순위 무변경) |
| `eval/video_planning_eval.md` | **신규 §2.A.1 depth_actionability** 평가 차원 추가 (기획 깊이·실행가능성, 0~1 스케일, real LLM/human 전용). §2 의 8 차원(0~5) 정의·스케일·가중치·산식 **무변경**. | **additive** (별도 축) |
| `eval/human_review_rubric.md` | **신규 §2.6 depth_actionability** 사람 채점 차원 추가 (0~1). §3.2 출력 형식에 `depth_actionability` 필드 추가. §2.1~2.5 (0~5) 정의·human_avg 산식 **무변경**. | **additive** (별도 축) |

## 2. 코드 영향

```
backend/fastapi/tests/test_eval_runner.py  — 의도 delta (count/priority 단언만):
  - test_load_golden_set_15_cases:        len 15→25, ids range 1~16→1~26.
  - test_load_golden_set_priority_grades: P0 7→8 / P1 6→12 / P2 2→5.
  - test_run_golden_set_eval_mock_passes: summary["total"] 15→25.
  ★ 그 외 러너 로직(_mock_envelope_for_case / score_case / check_thresholds / mode)·테스트 0 수정.

backend/fastapi/eval/golden_set_loader.py  — 무변경 (GS-XXX 동적 파싱 — 케이스 수 무관, 확대 시 코드 0 변경).
backend/fastapi/eval/runner.py             — 무변경 (mock-deterministic 채점 로직·차원 목록 불변).
```

★ **depth_actionability 는 코드(러너)에 채점 로직을 넣지 않는다.** mock-deterministic 러너는 plan
골격만 합성하므로 본 차원을 의미있게 채점할 수 없다(항상 ~0.2 부근으로 무의미). 따라서 본 차원은
`video_planning_eval.md` §2.A.1 / `human_review_rubric.md` §2.6 **문서(스펙)에만 정의**되며,
real LLM eval(mode='real') 또는 human review 에서만 채점된다. runner 의 §2 8 차원 structural 채점은
behavior-preserving (불변).

## 3. 회귀 안전 근거 (behavior-preserving)

- **golden_set additive ★**: GS-001~015 (id/name/input/expected_*/notes) 한 글자도 무변경.
  GS-016~025 는 신규 추가만. loader 는 케이스 수 무관 GS-XXX 파싱(ADR-033 §2.1) → 확대 시 코드 0 변경.
  신규 케이스도 §1 표준 형식 준수 → mock canonical fixture(_mock_envelope_for_case)가 동일하게
  3 plan / hook / flow / 광고·차단 0 을 합성 → schema 100% / pass 100% / gate PASS 유지.
- **우선순위 additive ★**: 기존 P0 7 (핵심 흐름/보안) 케이스 불변. 신규 분배 P0 +1 (GS-022 제품홍보
  광고차단 — 보안급 P0), P1 +6, P2 +3. §3 통과 임계(P0 100% / P1 ≥90% / P2 ≥80%) 정책 불변.
- **depth_actionability 별도 축 ★**: §2 8 차원(video_planning_eval)·§2.1~2.5(human_review)의
  정의·스케일·가중치·평균 산식(overall_score_avg / human_avg)에 **미포함**. 0~5 가 아닌 별도 0~1
  스케일로 분리 → 기존 평균/verdict 산식에 혼입 0. mock 러너 미채점 → mock eval baseline 불변.
- **운영 코드 0 수정 ★**: agents/(planning.py SYSTEM_PROMPT 포함)·orchestration/·routers/·schemas/
  ·db/·apps/web 전부 무변경. 본 CC 는 eval 문서 + test count/priority 단언만 변경 (검증 phase).
- **의도 delta (문서화)**:
  1. golden_set count 단언 15→25 (`test_load_golden_set_15_cases` / priority P0 8·P1 12·P2 5 / mock total 25).
  2. depth_actionability 차원 추가 (real/human 전용 — mock 러너 미채점, 코드 채점 로직 0).

## 4. 검증 결과

```
golden_set loader: load_golden_set() → 25 케이스 (GS-001~025) / priority P0 8·P1 12·P2 5 (확인).
eval-run (mock-deterministic, golden_set 25 케이스):
  schema 100% / pass 100% / structural 평균 1.0 / 광고 0% / 차단 0% / P0(8) 100% / gate PASS.
  ★ mock 채점 로직 불변 — 신규 10 케이스도 동일 canonical fixture → 동일 pass.
pytest backend/fastapi/tests/: 471 → 471 PASS (개수 불변 — 신규 test 0, count/priority 단언 delta만 in-place 수정).
운영 코드 변경: 0 (agents/orchestration/routers/schemas/db/apps 전부 무변경, planning.py SYSTEM_PROMPT 불변).
키 commit: 0.
```

## 5. Rollback

- `eval/golden_set.md`: GS-016~025 블록 + §0/§2 헤더/§3/§7/§9 v1.2.0 entry git revert → 15 케이스 복귀.
- `eval/video_planning_eval.md`: §2.A 블록 삭제 → 8 차원 복귀.
- `eval/human_review_rubric.md`: §2.6 블록 + §3.2 `depth_actionability` 라인 삭제 → 5 차원 복귀.
- `test_eval_runner.py`: count/priority 단언 25→15, P0 8→7·P1 12→6·P2 5→2 복귀.
- 복귀 후 mock eval baseline 불변 (default mock 경로 = CC-009 / Phase 10 상태).

## 6. 변경 이력

- 2026-06-02: Phase 12 Slice 1 — golden_set 15→25 확대 (도메인 다양성: 요리/뷰티/IT리뷰/운동/여행/
  교육/패션/반려동물/제품홍보/게임리뷰 × 길이 15s/30s/60s × intent quick/discovery)
  + depth_actionability 평가 차원 추가 (video_planning_eval §2.A.1 + human_review_rubric §2.6,
  real/human 전용, mock 러너 미채점) + test count/priority 의도 delta 문서화 (CC-011).
```
