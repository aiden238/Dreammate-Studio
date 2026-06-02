# Phase 14 — 진입 4점검 (Assumptions / Simplest Slice / Surgical Scope / Verification)

## 1. Assumptions (가정)
### 1.1 확정 가정
- 백엔드 endpoint 3종(`/plans/start`·`/plans/{id}/wizard/{step}`·`/plans/{id}/generate`) + client 함수(`startPlan`/`wizardStep`/`generateMultiPlan`/`getPlan`)가 **이미 존재** — 신규 endpoint 불필요(project-1 매핑 + 실측 확인).
- 생성 입력 단일 지점 = `moa_orchestrator.py:88` `plan_entry["initial_input"]`. → wizard_data 조립을 여기(또는 plans.py)에서 additive 처리하면 위저드 입력이 생성에 반영됨.
- rich gated(`rich_output_enabled`)는 `/generate` 경로 내부 처리 → 위저드가 이 경로를 쓰면 자동 상속(별도 배선 0).
- `/plan/[plan_id]` 는 GET `/plans/{id}` 로 백엔드 envelope 를 읽어 PlanCard rich 렌더 — 위저드 목적지로 재사용 가능.
- audit_naming: contract 변경이 S1 api_contract 한정 → S1 진입 시 `scripts/audit_naming.ps1` 실행 후 기록 (현 entry 는 contract 무변경).

### 1.2 불확실 항목 (phase-complete 시 검증)
- U-1: 위저드 step 입력(brand/domain/series/target/tone 선택 + direction)을 **하나의 user_input 문자열로 조립**했을 때 생성 품질이 랜딩 자유서술 대비 충분한가 (실 LLM 라이브로 확인).
- U-2: Quick(4) vs Discovery(7) 의 step 키 구조가 백엔드 `wizard_data[step]` 누적과 매끄럽게 매핑되는가 (step 명명: `step1..7` / `quick.initial|clarify|direction`).
- U-3: 위저드 인라인 PlanCard 제거 후 `/plan/[plan_id]` 라우팅 시 로딩 UX(30~60초 생성 대기) 자연스러운가.

## 2. Simplest Slice (3회 압축)
- 1차: "Quick(4) + Discovery(7) 둘 다 실연결 + 백엔드 wizard_data 소비 + /plan/[id]"
- 2차: "**Quick 위저드만** startPlan→wizardStep×→generateMultiPlan→/plan/[id] (Discovery 후속)"
- 3차: "**Quick generate 단계만**: 위저드가 수집한 입력으로 startPlan(initial_input)→generateMultiPlan→/plan/[id] (중간 step UI 현행, 최종 생성만 실연결)"
→ ★ Simplest Slice = **Quick 위저드 최종 단계의 실 생성 배선**(S2 의 핵심). 단, 백엔드 wizard_data 소비(S1)를 먼저 깔아 모든 step 입력이 반영되게 한다.

## 3. Surgical Scope
| 분류 | 파일 |
|---|---|
| editable | S1: `routers/plans.py` / `orchestration/moa_orchestrator.py`(wizard_data additive) + tests + (필요 시)`api_contract.md` · S2: `apps/web/app/new/quick/**` + `lib/*` · S3: `apps/web/app/new/discovery/**` + `lib/*` · S4: eval/retrospective/state |
| read-only (contract-change 필요) | `docs/contracts/api_contract.md` · `frontend_design_contract.md` · `output_schema.md` |
| forbidden | ★ `app/page.tsx`/`generate.py`/`dreammate.slice6.plan`(랜딩 byte-identical) · per-step P-001~P-005 LLM(PARKED) · `phases/archive/**` |

★ 모든 sub-agent prompt 에 P-X1 §SELF-VERIFICATION(git diff --stat ↔ editable/forbidden 비교) 포함.

## 4. Verification (acceptance 매핑)
- A1/A2-PP → S1 pytest(wizard_data 조립 + 랜딩 회귀 0, 499 유지).
- A3/A4/A6 → S2/S3 typecheck + 위저드 흐름.
- A5/A7/A8 → S4 라이브(rich ON) + 회귀 + 키 0 + close.
