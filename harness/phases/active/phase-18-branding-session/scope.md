# Phase 18 — Scope

## 포함 (in-scope)
- **S1**: `topic_discovery` agent — `ask`(상태→다음 질문+카드 2~4 or 종료) / `finalize`(상태→후보 주제 3×브랜딩 방향). prompt_registry 등록(prompt-version-review). 단위 test(mock).
- **S2**: branding endpoint — `POST /plans/{id}/branding/next`(답변→다음 질문/종료) + `.../finalize`(→후보3). 세션 상태(Q&A)를 plan_entry.wizard_data.branding 누적. (agent-io-check)
- **S3**: frontend `/new/branding` — 질문 카드 + 자유입력 + 진행바 → 후보 3 카드 → 택1 → `/plan/[id]`.
- **S4**: planning 연결(택1 topic/방향 → initial_input/approved_direction) + **brand_memory 시드**(gated, Phase 17 BrandMemoryRepo 재사용, 자동 승격 X).
- **S5**: 라이브 e2e(스무고개→주제→생성, PKM 반영) + phase-complete.

## 예상 파일 변경
| 분류 | 경로 |
|---|---|
| editable | `backend/fastapi/agents/topic_discovery.py`(신규) · `routers/plans.py` 또는 신규 branding 라우터 · `apps/web/app/new/branding/`(신규) · `apps/web/lib/api.ts` · tests · phase/state/meta |
| read-only (→contract-change) | `docs/contracts/*` · `ai_system/prompts/prompt_registry.md`(P-신규 등록) |
| forbidden | `phases/archive/*` · commercial_viral · 영상 제작 |

## gated/additive 원칙
- 신규 진입·endpoint·agent·page **추가만** — Quick/Discovery/planning/output 무변경(byte-identical).
- brand_memory 시드 = Phase 17 governance 계승(≥0.9/proposal, 자동 승격 X).
- 자유입력 = 기존 Intent(P-001) + llm_security 차단 재사용.
