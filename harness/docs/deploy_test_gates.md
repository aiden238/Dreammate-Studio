# Deploy Test Gates A~G (배포 테스트 게이트 — Phase 10 준비)

> 작성: Phase 10 (MVP 통합 테스트) Slice 4
> 상태: **준비(prep) 문서** — 각 게이트의 통과 조건 + 현 준비 상태. 실 배포·운영(SQL function 등)은 운영 단계 (NG11).
> 목적: MVP end-to-end 통합 완료 → 알파/베타 진입 전 게이트 정의.

---

## 게이트 개요

| Gate | 이름 | 목적 | 현 준비 상태 |
|---|---|---|---|
| **A** | Local Smoke Test | 로컬에서 전체 흐름 동작 | ✅ **준비됨** (smoke_test_phase_10 12/12 + pytest 381 + 통합 test) |
| **B** | Staging 배포 | staging 환경 배포 + 기동 | 🟡 준비 (env/secret 주입 절차 + 배포 스크립트 필요) |
| **C** | 내부 알파 테스트 | 팀 내부 손-검증 (manual smoke) | 🟡 준비 (manual smoke 체크리스트 §C) |
| **D** | Beta Staging | 베타 환경 + 실 LLM eval opt-in | 🟡 준비 (실 LLM mode capability 有 — 키 주입 시 활성) |
| **E** | 제한 사용자 테스트 | 소수 실사용자 + 피드백 수집 | ⬜ 미준비 (사용자 모집/동의 + 모니터링) |
| **F** | 비용 / 성능 테스트 | LLM 비용 + latency 측정 | 🟡 준비 (cost-review Skill + eval latency 차원, 실 LLM 활성 필요) |
| **G** | Production Readiness | 운영 배포 최종 게이트 | ⬜ 미준비 (보안 audit + RLS 운영 + SQL function + 백업) |

---

## A — Local Smoke Test ✅
- 통과 조건: pytest 전체 green + smoke_test_phase_N 전체 PASS + scenario_simulation PASS + 통합 test green.
- 현 상태: **PASS** — pytest 381 / smoke_test_phase_10 12/12 / scenario_sim v8 36/36 / test_integration_mvp 12 / eval-run mock gate PASS.
- 산출: `scripts/smoke_test_phase_10.ps1`, `tests/test_integration_mvp.py`, `eval/regression_results/phase-10_baseline.md`.

## B — Staging 배포 🟡
- 통과 조건: staging 환경 변수/secret(.env — ★ user-provided) 주입 + FastAPI/Next.js 기동 + Supabase 연결 + health check.
- 준비 항목: 배포 스크립트(미작성) / env 주입 절차(키 커밋 0 — .env user-provided) / Supabase 마이그레이션 0001~0005 적용 / `match_approved_knowledge` SQL function 정의(NG11 — 운영 단계).
- ★ 키/자격증명은 저장소 미포함 — staging secret store 주입.

## C — 내부 알파 테스트 🟡
- 통과 조건: 팀 내부 manual smoke (Discovery+Quick 실 흐름 손-검증) + 주요 UX 경로 확인.
- manual smoke 체크리스트: ① Quick 입력→3안→선택→피드백 ② Discovery wizard 7단계 ③ SSE progress 표시 ④ 피드백 PII 마스킹 ⑤ graceful(외부 실패) ⑥ 모바일 화면.
- (자동 smoke=Gate A 와 분리 — Gate C 는 사람 검증.)

## D — Beta Staging 🟡
- 통과 조건: 베타 환경 + ★ **실 LLM eval mode opt-in 활성**(OPENAI/ANTHROPIC 키 주입) → 실 품질 측정 baseline.
- 준비: 실 LLM eval mode capability 구축 완료(Phase 10 S3) — 키 주입 시 `EVAL_MODE=real` 활성. 실 LLM 품질 회귀 baseline 수립.

## E — 제한 사용자 테스트 ⬜
- 통과 조건: 소수 실사용자 + 동의 + 피드백 수집 + brand_memory_extractor 실 데이터 누적.
- 준비 필요: 사용자 모집/동의 절차 / 모니터링(agent_io_logs) / 피드백 루프(P-AUX-2 활성 — Phase 10 S2 구축).

## F — 비용 / 성능 테스트 🟡
- 통과 조건: LLM 비용/요청 + latency 임계 만족 (eval-run §6 비용·latency 게이트).
- 준비: cost-review Skill(미트리거 — Phase 9+ 대기) + eval latency/cost 차원(실 LLM 활성 필요). 비용 폭탄 방지 rate_limit 확인.

## G — Production Readiness ⬜
- 통과 조건: 보안 audit(전체) + RLS 운영 검증(pgtap) + SQL function 정의 + 백업/롤백 + 모니터링/알림.
- 준비 필요: security-review 전체 회차 / RLS 실 DB 검증 / `match_approved_knowledge` 정의 / 운영 rollback_policy 활성 / 비용 알림.

---

## 게이트 진행 원칙
- A → B → C → D → E → F → G 순차 (각 게이트 통과 후 다음).
- 현 Phase 10 완료 시점: **Gate A 통과**, B~D 준비, E/G 미준비(운영 단계).
- 실 LLM/실 배포/운영 항목은 키·인프라(user-provided) + 별도 운영 phase.
