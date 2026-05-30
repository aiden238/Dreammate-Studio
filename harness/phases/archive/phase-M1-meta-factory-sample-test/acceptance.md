# Phase M1 — Acceptance (A1~A8 + MG1~MG3)

> dry-run 1회. 판정은 통과/실패가 아니라 **각 검증 차원 PASS/FAIL/PENDING/GAP** (GPT 보완 ②).

## A1~A8 (산출물 + 검증)

| ID | 항목 | 검증 방법 | Slice |
|---|---|---|---|
| **A1** | 팟캐스트 `domain_brief.md` 가 `domain_brief_schema` 필수 필드 충족 (도메인 정의 + forbidden_scope) | 파일 존재 + schema 필드 매칭 | S1 |
| **A2** | `harness_blueprint.md` + 6 scaffold draft 생성 (`harness_blueprint_schema` 형식, validation 3필드 슬롯 포함) | 파일 7개 존재 + schema 섹션 | S1 |
| **A3** | `validation_workflow` 6 검증 전부 실행 + 각 **PASS/FAIL/PENDING/GAP** 기록 | sample_test_podcast_validation.md 6 섹션 + 4상태 명시 | S2 |
| **A4** | **with/without 6 지표 수치표** (누락파일/forbidden_scope/Skill충돌/cross-ref누락/eval gate/proposal-first) | 수치 표 (주관 서술 0) | S2 |
| **A5** | GAP 목록 + 보완 제안을 `outputs/TEST/sample_test_podcast_validation.md` 에 기록 | GAP 섹션 + proposal | S2 |
| **A6** | 현재 하네스 5 gaps(M0 blueprint) 가 팟캐스트 도메인에서 **재현되는지** 명시 | 5 gaps 재현 표 | S2 |
| **A7** | dry-run 결과를 통과/실패 이분법 아닌 4상태로 종합 + 다음 개선 입력 도출 | 판정 종합 섹션 | S2 |
| **A8** | 결과 요약 — 변경 파일(전부 outputs/) + 6검증 결과 + GAP + 다음 단계 | 보고 + (별도) retrospective | S2/doc-sync |

## MG1~MG3 (메타 — 강제 게이트)

| ID | 항목 | 검증 |
|---|---|---|
| **MG1** ★★ | dry-run 변경이 `meta_factory/outputs/TEST/**` **외부 0줄** | `git diff --stat` 에 `outputs/TEST/` 외 경로 0 (GPT 보완 ③ + TEST 격리) |
| **MG2** | FastAPI/Next.js/Supabase **0줄** | `git diff backend/ apps/web/ migrations/` = 0 (A9) |
| **MG3** | P-X1 §SELF-VERIFICATION **52연속 PASS** | S1·S2 각 sub-agent git status/diff + forbidden 검사 |

## ★ 4상태 정의 (GPT 보완 ②)

```
PASS    — 검증 기준 충족
FAIL    — 기준 위반 (즉시 보완 필요, blueprint active 불가)
PENDING — 판정 보류 (예: with_without_skill_eval 은 소표본 → 초기 PENDING 정상, fail 아님)
GAP     — machinery/blueprint 의 구조적 부족점 (improvement_reports 로 다음 개선 입력)
```

> ★ `with_without_skill_eval`(검증 4) 과 `eval-run 연동`(검증 5) 은 dry-run 소표본 특성상 **PENDING/GAP 가 기본 예상**. 이를 fail 로 처리하지 않는다.

## 검증 5 (eval-run 연동) 의 dry-run 범위

- 실 LLM 대량 호출 없이 **절차 적용 가능성**까지 확인: golden_set 케이스 형식이 팟캐스트 harness 에 매핑 가능한가 / schema 준수율·임계값 게이트가 phase 종료 차단으로 연결 가능한가.
- 실측 점수가 없으므로 검증 5 결과는 **PENDING (절차 적용 가능 / 실측 미수행)** 으로 기록 가능 — NG7 정합.

## 회귀 baseline (M0 → M1)

| 지표 | Phase M0 | M1 목표 |
|---|---|---|
| pytest | 339/339 | **339 유지** (런타임 0) |
| FastAPI/Next/Supabase 변경 | 0줄 | **0줄 (A9/MG2)** |
| ★ dry-run `outputs/TEST/` 외 변경 | — | **0줄 (MG1 — 본 phase 신규 게이트)** |
| component_map.md 0줄 streak | 45 | **유지** |
| PlanCard.tsx 0줄 streak | 35 | **유지** |
| P-X1 streak | 50 | **52** |
| Skill 수 | 21 | **21 유지** (신규 Skill 0 — 기존 harness-factory 사용만) |
| harness-factory 트리거 | 0 (proposal-only 등록만) | **첫 실트리거** (S1·S2) — skill_usage_log 기록 |

## qa-check 카테고리 (M1 final 예상)
- 1 제품/범위 PASS (outputs-only — 범위 정확) / 2 AI 구조 skip / 3 RAG skip / 4 프론트 skip(변경 0) / 5 평가 **부분**(검증 5 절차 적용 가능성 — PENDING) / 6 **메타 PASS** (★ 핵심 — machinery 실작동) / 7 컨텍스트 / 8 큰 결정 skip(신규 contract 0) / 9 Phase 운영 PASS / 10 보안 skip / 11 비용 skip(LLM 대량 호출 0)
- **예상**: 4 PASS / 1 부분 / 6 skip (dry-run meta-phase 특성).
