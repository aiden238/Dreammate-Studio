# Phase 13 — Closing Notes (출력 확장 — Output Enrichment, compact→rich)

> 종료일: 2026-06-03
> 결과: ✅ compact(7필드)→rich(12 슬롯) 출력 확장을 **gated 로 안전하게** 운영 반영 — 깊이 0.231→1.000(≥0.8 PASS, OFF byte-identical) + Critic depth(88점 함정 해소) + frontend rich + ★ 라이브 입증(/generate end-to-end rich, HTTP 200). pytest 471→499(기존 471 수정 0 = OFF 회귀 0). 키 0.
> 유형: 제품 phase (런타임 有 — ★ 이 프로젝트 첫 의도적 출력 변경) — gated 단계 롤아웃 + additive 스키마(flag OFF byte-identical, behavior-preserving)

## 산출물 (Entry + 6 Slice)

- **Entry (`aaf4641`)**: Phase 12 종료(archive) + Phase 13 entry 8파일. gated+full 롤아웃 정의.
- **S1 (`1665dc0`, CC-012)**: output_schema rich 12 슬롯 additive(`Plan` 9 + `PlanFlowBeat` 3, 전부 Optional) + `model_dump_compact()` + 상수 2종 + output_schema §8.1 v1.1.0→v1.2.0 + agent-io-check PASS + test 10 → pytest 471→481.
- **S2 (`ed1cf1f`, CC-013)**: planning `RICH_SYSTEM_PROMPT` + rich build 헬퍼 + `RICH_PROMPT_VERSION=v1.1.0` + prompt_registry P-006 v1.0.0→v1.1.0(gated 공존) + test 5 → 481→486. compact 보존 + rich 미연결(behavior-preserving).
- **S3 (`339da50`, CC-014)**: gated wiring — config `rich_output_enabled` default False + `envelope_to_response_dict()` + planning 프롬프트 분기 + generate/orchestrator/plans 직렬화 분기. OFF=compact byte-identical / ON=rich + revise 왕복 rich 보존 + test 7 → 486→493(기존 486 수정 0).
- **S4 (`61029cc`, CC-015)**: Critic depth — `RICH_SYSTEM_PROMPT`(9차원) + `DIMENSIONS_RICH` + `RICH_PROMPT_VERSION=v1.2.0` + `run_critic` 분기(ON=9차원, OFF=8차원) + prompt_registry P-007 v1.1.0(active)+v1.2.0(gated) + agent-io-check PASS + test 6 → 493→499. 88점 함정 해소.
- **S5 (`9ec2783` + `11a2386`)**: frontend — `lib/types.ts` rich optional + PlanCard rich 조건부 8섹션(값 있을 때만, compact=0개=기존 동일) 순수 additive. + 품질점수(Critic 배지) 미표시(`SHOW_QUALITY_SCORE` flag, 사용자 요청). backend 0, design.md 준수.
- **S6 (본 close)**: cost 재조정(CC-016 — rich 3~5배 × 3안 + B-RES-1 통합) + 깊이 재측정(`eval/regression_results/2026-06-03_phase-13-s6-depth-remeasure.md` — OFF 0.231 / ON 1.000, ≥0.8 PASS) + phase-complete(retrospective + 본 closing + archive + REGISTRY/PROJECT_STATE done + patterns).

## S1~S6 완료

| Slice | 상태 | 비고 |
|---|---|---|
| Entry | ✅ | entry 8파일 (multi-llm self 12th = entry 단계 deferred, 본 phase 생략 명시) |
| S1 | ✅ | output_schema rich 12 슬롯 additive (CC-012) |
| S2 | ✅ | planning rich 프롬프트 P-006 v1.1.0 gated (CC-013) |
| S3 | ✅ | gated wiring rich_output_enabled OFF byte-identical (CC-014) |
| S4 | ✅ | Critic depth 9차원 88점 함정 해소 (CC-015) |
| S5 | ✅ | frontend PlanCard rich 조건부 8섹션 + 품질점수 숨김 |
| S6 | ✅ | cost 재조정(CC-016) + 깊이 재측정 OFF 0.231/ON 1.000 + close |

## 최종 baseline

| 지표 | Phase 12 final | Phase 13 final |
|---|---|---|
| pytest | 471 | **499** (+28: S1 10 + S2 5 + S3 7 + S4 6, 기존 471 수정 0 = OFF byte-identical) |
| 깊이 (운영 run_planning) | (측정 전용 1.0) | **OFF 0.231 / ON 1.000 (≥0.8 PASS, 4/4 편차 0)** |
| 출력 스키마 | compact 7필드 | **rich 12 슬롯 additive** (gated, OFF=compact byte-identical) |
| Critic 차원 | 8 | **8(OFF) / 9(ON gated, +depth_actionability)** — 88점 함정 해소 |
| frontend | compact PlanCard | **rich 조건부 8섹션** (값 있을 때만, compact=기존 동일) + 품질점수 숨김 |
| 라이브 | — | **/generate end-to-end rich HTTP 200** (rich 9슬롯 + beat visual/dialogue/caption) + 화면 rich 확인 |
| contract-change | CC-011 | **CC-012~CC-016** (Phase 13 만 5 CC, 누적 17회) |
| rich default | — | ★ **OFF 유지 (전환 미결정 — non_goal, 사용자 opt-in / Phase 14)** |
| 키 commit | 0 | **0 유지** |
| PlanCard / component_map 0줄 | 35 / 45 | PlanCard rich 추가(additive) / component_map 0줄 유지 |

## ★ 미결정 / 미완 (Phase 14 후보)

- ★ **rich default 전환 미결정** (non_goal) — Phase 13 은 gated OFF 유지(검증·라이브 입증까지). flag default ON(전 사용자 rich) 전환은 **별도 결정** — cost(CC-016 — 3~5배 × 3안, tier 유료/opt-in 권고) + 품질(feature 존재 ≠ 우수성) 합의 후. 사용자 opt-in / Phase 14 후속.
- ★ **위저드(/new/*) ↔ 백엔드 실연결 미완** — 랜딩 `/` 만 실 생성(/generate) 경로, Discovery/Quick 위저드(/new/*)는 여전히 mock. rich 라이브는 `/` 경로로 입증 — 위저드 실연결은 Phase 14 후보.
- **품질점수 숨김** — Critic 품질 배지 미표시(`SHOW_QUALITY_SCORE` flag, 사용자 요청). 재노출 시 flag 토글.
- **품질 보강 deferred** — feature 존재(0/1) ≠ 콘텐츠 우수성. human review 실 채점(Phase 12 S4 kit) + 전수(25) 실 LLM eval baseline.

## ★ 사용자 보고 형식

| 항목 | 내용 |
|---|---|
| 변경 파일 (S6 운영 코드) | **0** (S6 = 문서/종료만 — 깊이 재측정 리포트 + cost CC + phase-complete) |
| Phase 13 누적 운영 코드 | schemas/output.py + planning.py + critic.py + config.py + generate.py + moa_orchestrator.py + plans.py (전부 additive/gated 분기) + frontend lib/types.ts + PlanCard.tsx |
| 핵심 | compact→rich 출력 확장을 gated 로 안전하게 — 깊이 0.231→1.000(≥0.8) + 88점 함정 해소 + frontend rich + 라이브 입증 |
| 런타임 변경 (OFF 회귀) | **0** — behavior-preserving(flag OFF byte-identical, 기존 471 test 수정 0), pytest 499 green |
| 라이브 | /generate end-to-end rich HTTP 200 + 화면 rich 확인 |
| rich default | **OFF 유지 (전환 미결정)** — 사용자 opt-in / Phase 14 |
| 다음 | **Phase 14 pending_user_decision** — rich default 전환 / 위저드 실연결 / 배포 Gate B~G |

## Phase 14 연결

- **Phase 14 = pending_user_decision** — 후보:
  - rich default 전환 결정(flag default ON, cost/품질 합의 후) / 위저드(/new/*) ↔ 백엔드 실연결 / 배포 Gate B~G(staging→운영) / Phase 12 S4 human review 실 채점 + 전수 실 LLM eval / B안 정식화 잔여(B-RES-2 ADR / B-RES-3 contract-change).

## Phase 1~13 총괄
```
Phase 0    : 하네스 마이그레이션
Phase 1~4  : MVP 기본 + PWA + FastAPI
Phase 4.5~6: Critic revise + Output Schema 안정화
Phase 5/5.5: DB/Auth/RLS/SSE + Legacy 통합
Phase 7    : RAG Lite     Phase 8 : MOA orchestrator     Phase 9/9.5 : 결과저장+피드백 + eval-run
M0~M3      : Meta-Factory (self-improvement loop 완주)
Phase 10   : MVP end-to-end 통합 + 배포 Gate A ✅
Phase 11   : LLM Gateway A안+B안 (alias→provider + 3-provider 3안 라이브) ✅
Phase 12   : 검증 페이즈 — 깊이 격차 4.3x 실측 ✅
Phase 13   : 출력 확장 — compact→rich gated(깊이 0.231→1.000, 88점 함정 해소, frontend rich, 라이브 입증) ✅
→ 다음 = Phase 14 pending_user_decision (rich default 전환 / 위저드 실연결 / 배포 Gate B~G).
```
