# Phase M1 — Goals (Meta-Factory Sample Test)

> Phase: phase-M1-meta-factory-sample-test
> 유형: **meta-phase** (제품 phase 아님 — L3 Meta-Factory machinery 1회 dry-run 검증)
> 진입일: 2026-05-31
> 예상 시간: 2.5~4h (S1 generation + S2 validation, 모두 sub-agent dispatch)
> ★ 런타임 변경 0 (FastAPI/Next.js/Supabase 0줄) + ★★ **dry-run은 `meta_factory/outputs/` 외부 변경 0** (GPT 보완 ③)
> 결정 근거: Phase M0 (ADR-035) machinery 의 실작동 증명 / GPT M0 검토 §2·§5 보완

## 한 줄 정의

Phase M0 가 만든 **meta_factory machinery**(`generation_workflow.md` 11단계 + `validation_workflow.md` 6검증)를, Dreammate(영상기획)와 **인접하지만 다른** 도메인 1개 — **「팟캐스트 에피소드 기획 AI」** — 에 **1회 dry-run** 으로 적용하여 다음 두 질문에 답한다:

```
Q1. meta_factory 가 실제로 새 도메인 harness blueprint 를 만들 수 있는가?  (generation_workflow)
Q2. validation_workflow 가 실제로 그 blueprint 를 검증할 수 있는가?         (6 검증)
```

★ **목적은 "성공"이 아니라 "GAP 발견"이다.** 첫 dry-run 은 fail/pending 이 나와도 정상이며, 어디가 부족한지를 `improvement_reports/` 에 남기는 것이 본 phase 의 산출이다 (GPT 보완 ②).

## 3계층 위치 (L1/L2/L3)

```
L1 Product Runtime         : 변경 0 (A9 — dry-run 은 런타임 무관)
L2 Implementation Harness  : 변경 0 (dry-run 중 — phase 등록/회고는 ★별도 doc-sync 로 분리, GPT 보완 ③)
L3 Meta-Harness Factory    : machinery 를 ★실행 — 입력 domain_brief → 출력 blueprint → 6 검증 → GAP 리포트
                             ★ 모든 산출물은 meta_factory/outputs/TEST/ (TEST 폴더 격리, active 아님)
```

## 핵심 목표 (G1~G6)

| ID | 목표 | 검증 (acceptance) |
|---|---|---|
| **G1** | 팟캐스트 `domain_brief` 작성 (`domain_brief_schema.md` 형식 — forbidden_scope 포함) | A1 |
| **G2** | `generation_workflow.md` 11단계 실행 → `harness_blueprint.md` (`harness_blueprint_schema.md` 형식) + 6 scaffold draft 생성 | A2 |
| **G3** | `validation_workflow.md` 6 검증 실행, 각 차원 **PASS/FAIL/PENDING/GAP** 4상태 기록 (GPT 보완 ②) | A3 |
| **G4** | **with/without 비교를 6 지표로 수치화** (주관 평가 금지, GPT 보완 ①) | A4 |
| **G5** | GAP 목록 + 보완 제안을 `outputs/TEST/sample_test_podcast_validation.md` 에 기록 (proposal-first) | A5 |
| **G6** | blueprint 5 gaps(M0 blueprint 가 명시한 현재 하네스 부족점)가 새 도메인에서도 재현되는지 확인 | A6 |

## 메타 목표 (MG1~MG3)

| ID | 목표 |
|---|---|
| **MG1** | ★★ dry-run sub-agent 의 변경이 `meta_factory/outputs/TEST/**` **외부 0줄** (GPT 보완 ③ + TEST 폴더 격리 강제 게이트) |
| **MG2** | A9 — FastAPI/Next.js/Supabase **0줄** |
| **MG3** | P-X1 §SELF-VERIFICATION **52연속 PASS** (M0 50 + M1 S1·S2 2) |

## with/without 6 지표 (GPT 보완 ① — 수치화)

| # | 지표 | 측정 | 기대 (with vs without) |
|---|---|---|---|
| 1 | 누락된 필수 파일 수 | acceptance §1 최소 구조 대비 누락 개수 | with < without |
| 2 | forbidden_scope 반영 여부 | domain_brief.forbidden_scope → non_goals/라우터 금지 매핑 (0/1) | with=1, without 흔히 0 |
| 3 | Skill trigger 충돌 수 | description 키워드 중첩 개수 | with < without |
| 4 | contract cross-ref 누락 수 | prompt↔output / api↔front / db↔migration / agent_io 누락 개수 | with < without |
| 5 | eval gate 존재 여부 | 임계값 게이트가 phase 종료/배포 차단으로 연결 (0/1) | with=1, without 흔히 0 |
| 6 | proposal-first 위반 여부 | active 자동 반영 시도 / outputs 외 변경 (0=위반없음) | with=0 |

- **without** = AGENTS/CLAUDE/meta_factory 문서를 **보지 않고** 일반 프롬프트로 팟캐스트 하네스 구조 작성.
- **with**  = `domain_brief_schema` + `generation_workflow` + `validation_workflow` + `templates` + `harness-factory` Skill 절차 사용.

## 사용자 가치 (Why)

- **machinery 실작동 증명**: M0 는 "문서·skeleton만" 상태. 본 phase 로 "실제로 도는가"를 1회 입증.
- **범용성 1차 검증**: 인접 도메인(팟캐스트)에서 6 패턴/scaffold/검증이 재사용되는지 확인 (완전 이질 도메인은 실패 원인 분석 곤란 → 인접부터).
- **다음 개선 입력**: GAP 리스트 = M0 machinery 의 다음 보강 항목 (payoff deferred 의 실측 근거).
```
