# Phase 12 — Acceptance (A1~A8 + MG1~MG3)

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | **golden_set ~25 확장** — 15→~25 (신규 ~10, 기존 15 회귀 보존), contract-change 경유(★ additive) | golden_set.md 케이스 수 + CC 로그 | S1 |
| **A2** | **depth/actionability 차원 rubric 추가** — eval rubric 에 깊이·실행가능성 평가 차원 정식 등록(★ additive, 기존 차원 보존) | rubric diff + CC 로그 | S1 |
| **A3** | **실 LLM eval 1회 실행 + 차원별 점수 리포트 저장** — 현 compact 운영 프롬프트 기준선 on golden_set ~25 → 차원별 실 품질 점수 + 임계값 판정 | `eval/regression_results/phase-12-*` 저장 | S2 |
| **A4** | **깊이 격차 수치 도출** — compact vs rich 비교, 구체 metric(필드수 / beat 깊이 / 대사·자막·샷·썸네일 유무 / 토큰 / 실행가능성) → "현재 깊이 X / 잠재 Y / gap Z" | 깊이 격차 분석 리포트 | S3 |
| **A5** | **human review kit 준비** — 표본 셋 + rubric 채점 시트 + LLM 점수 대조 설계 (★ 사용자 실 채점은 deferred — kit 까지가 acceptance) | human review kit 산출 | S4 |
| **A6** | **S5 종합 리포트 + Phase 13 우선순위** — MO1~MO3 종합 + 깊이 격차 결론 + 확장 ROI/우선순위(Phase 13~20 데이터 근거) | `meta/retrospectives/phase-12.md` | S5 |
| **A7-PP** | **behavior-preserving** — ★ 운영 endpoint/agent/prompt/output_schema 0 수정. pytest 471 유지 | git diff 운영 .py 0 + pytest 471 green | 전 Slice |
| **A8** | **키 0** — 실 LLM 호출은 사용자 승인 비용, 키 평문 commit 0 (.env user-provided) | `git diff | grep sk-/AIza` 0 | S2 |

## MG1~MG3 (메타)
| ID | 항목 | 검증 |
|---|---|---|
| **MG1** | multi-llm-validation self-form (11th, V1~V6) — Phase 12 진입 타당성 | `meta/validations/2026-06-02_phase-12-pre-entry_self.md` |
| **MG2** | contract-change — golden_set 확장 + eval rubric depth/actionability 차원(★ additive) | `docs/contract_changes/2026-06-02_phase-12-eval-depth.md` (S1) |
| **MG3** | P-X1 §SELF-VERIFICATION 연속 유지 (운영 코드 0 + behavior-preserving) | sub-agent/commit 검사 (전 Slice) |

## ★ behavior-preserving 게이트 (A7-PP — Phase 12 핵심)
```
운영 코드 0 수정 — backend/fastapi/** , apps/web/**  (Phase 12 = 측정·문서만)
운영 prompt_registry / output_schema / agent_io 0 변경 (S1 의 eval golden_set/rubric 만 예외, contract-change additive)
eval 은 측정 capability(runner 직접 실행) — 운영 endpoint/agent 미경유
검증: pytest 471 전부 green (신규 test 0 — 문서·eval 데이터만, 운영 .py 0)
```

## ★ 깊이 격차 측정 게이트 (A4 — 이번 phase 의 중심 산출)
```
입력: 같은 모델(gpt-4o-mini) · golden_set 표본
  compact = 현 운영 프롬프트 (name/concept/hook/2~4 beat/pros/risks 7필드)
  rich    = 확장 측정-프롬프트 (hook 3변형·타임코드·대사·자막·B-roll·썸네일/제목·CTA·레퍼런스·길이 변형)
metric (구체):
  필드수 / beat 깊이(평균 beat 수·서술 길이) / 대사·자막·샷·썸네일 유무(boolean 커버리지) /
  출력 토큰 / 실행가능성(actionability rubric 점수)
산출: "현재 깊이 X / 잠재 Y / gap Z" + 차원별 격차 → Phase 13 우선순위 근거
★ rich = 측정 전용 (운영 prompt/schema 0 반영) + 기획 브리프 경계 유지(완성 대본 아님)
```

## ★ 실 LLM eval 게이트 (A3·A8 — 실비용)
```
실 LLM eval 1회 실행 (사용자 승인 비용) on golden_set ~25, 현 compact 기준선
  → 차원별 실 품질 점수 + 임계값 판정 + regression_results/phase-12-* 저장
mock-deterministic eval = CI 회귀 게이트로 유지 (real 은 측정 전용, NG9)
키 0: .env user-provided, 평문 commit 0 (push 전 git diff grep sk-/AIza 점검)
```

## 회귀 baseline (Phase 11 → Phase 12)
| 지표 | Phase 11 final | Phase 12 (entry 기준) |
|---|---|---|
| pytest | 471 | **471 유지** (문서·eval 데이터만, 운영 .py 0) |
| 운영 코드 변경 | (B안 additive) | **0** (측정·계획 phase) |
| golden_set | 15 | **~25 예정** (S1, ★ entry 단계 0 — 사전 변경 금지) |
| eval 차원 | (Phase 10 rubric) | **+depth/actionability 예정** (S1, contract-change) |
| 실 LLM eval | capability(default off) | **측정 1회 실행 예정** (S2, baseline) |
| 깊이 격차 | (미측정) | **수치 도출 예정** (S3, compact vs rich) |
| human review | (미준비) | **kit 준비 예정** (S4, 실 채점 deferred) |
| 키 commit | 0 | **0 유지** |
| PlanCard / component_map 0줄 | 35 / 45 | **유지** (frontend 0 변경) |

## qa-check (Phase 12 — release gate)
- 검증/계획 phase — 운영 코드 0 수정이라 대부분 카테고리 **skip**(spec/measurement phase). behavior-preserving(pytest 471) + 키 0 + product_boundary(기획 브리프) 게이트 PASS 예상. eval 데이터·분석·human kit 산출 중심.
