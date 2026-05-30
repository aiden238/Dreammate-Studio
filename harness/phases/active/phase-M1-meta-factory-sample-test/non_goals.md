# Phase M1 — Non-Goals

## 명시적 제외 (NG1~NG12)

| ID | 항목 | 사유 |
|---|---|---|
| **NG1** | FastAPI/Next.js/Supabase runtime 변경 | dry-run — 런타임 무관 (A9) |
| **NG2** | 생성된 팟캐스트 harness 를 active 로 전환 / 실제 2nd 프로젝트 시작 | proposal-first — outputs/ 에 머무름 (factory_contract 규칙 7) |
| **NG3** | 기존 하네스(L2) 직접 변경 — AGENTS/CLAUDE/PROJECT_STATE/contracts/Skill | dry-run 은 읽기만 (GPT 보완 ③) |
| **NG4** | machinery 문서 변경 (generation/validation_workflow, schema, templates, blueprint) | M0 산출물 — 본 phase 는 **사용**만, 수정은 별도 contract-change |
| **NG5** | 자동 generator 코드 작성 | M0 NG11 계승 — skeleton·검증까지만 |
| **NG6** | 완전 이질 도메인(예: 금융/의료) 으로 first dry-run | 실패 원인 분석 곤란 — 인접 도메인(팟캐스트) 먼저 |
| **NG7** | 실제 LLM 대량 호출 / 비용 발생 평가 | dry-run — 추론·mock 기반 설계 검증 (검증 5 eval-run 은 절차 적용 가능성 확인까지) |
| **NG8** | with/without 비교를 **주관 서술**로 처리 | ★ 6 지표 수치화 강제 (GPT 보완 ①) |
| **NG9** | 첫 dry-run 결과를 "성공/실패" 이분법으로 판정 | ★ PASS/FAIL/PENDING/GAP 4상태 (GPT 보완 ②) |
| **NG10** | phase 등록/회고/archive 를 dry-run sub-agent 안에 포함 | ★ 별도 doc-sync 분리 (GPT 보완 ③) |
| **NG11** | golden_set / eval contract 변경 | 읽기만 — 검증 5 는 eval-run 절차 **적용 가능성** 확인 |
| **NG12** | 영상/오디오 자동 편집·TTS·BGM·async·A/B | MVP/Phase 11+ |

## ★ 핵심 원칙 (3)

1. **outputs-only**: dry-run 의 모든 쓰기는 `meta_factory/outputs/**` 에만. 외부 0줄 (MG1).
2. **GAP-first**: fail/pending 은 정상. 목적은 GAP 수집 (improvement_reports). with_without_skill_eval 은 소표본이라 **초기 PENDING 정상** — fail 로 보지 않음 (GPT 보완 ②).
3. **분리**: dry-run(sub-agent, outputs only) ↔ phase 운영(main 세션, 별도 doc-sync) 을 commit 단위로 분리 (GPT 보완 ③).

## 회피 패턴
- ❌ "blueprint 좋으니 바로 active 로" → NG2 (proposal-first 위반 = with/without 지표 6 fail)
- ❌ "machinery 가 부족하니 김에 generation_workflow 도 고치자" → NG4 (별도 contract-change)
- ❌ "phase 니까 PROJECT_STATE 도 sub-agent 가 갱신" → NG10 (별도 doc-sync)
- ❌ "with 가 더 좋아 보인다" (수치 없이) → NG8 (6 지표 수치 필수)
- ❌ runtime/기존 하네스 1줄 변경 → NG1/NG3 (A9/MG1 위반)
