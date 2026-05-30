# Phase M0 — Non-Goals

## 명시적 제외 (NG1~NG14) — 사용자 지침 §2/§7 + 제 정제

| ID | 항목 | 사유 |
|---|---|---|
| **NG1** | FastAPI runtime 코드 수정 | 메타 레이어 — 런타임 무관 |
| **NG2** | Next.js UI 코드 수정 (PlanCard·component_map 포함 ★) | |
| **NG3** | Supabase migration 추가 | |
| **NG4** | 기존 product 기능 추가 | |
| **NG5** | P-AUX-2 Brand Memory extractor agent 구현 | 사용자 결정 5 (Phase 10+) |
| **NG6** | 기존 `.claude/skills/` 대량 변경 (harness-factory 신규 외) | INDEX 충돌 규칙 |
| **NG7** | 기존 contracts 직접 변경 (api/output_schema/agent_io/db_schema 등) | contract-change 경유, 본 phase는 INDEX만 |
| **NG8** | PROJECT_STATE.md 큰 폭 임의 수정 | meta-phase 등록 최소 갱신만 |
| **NG9** | 기존 phase archive 무단 참조 후 구조 변경 | 참조만 (blueprint 역정리용) |
| **NG10** | meta_factory 결과물 기존 하네스 자동 반영 | proposal-first — outputs/ + proposals/에 먼저 |
| **NG11** | **실제 자동 generator 코드 작성** | skeleton·contract·validation 기준까지만 |
| **NG12** | `.claude/agents/` 자동 생성 | 다음 phase |
| **NG13** | 다른 도메인 하네스 실제 생성 | 다음 phase (validation 통과 후) |
| **NG14** | 영상 자동 편집 / TTS / BGM / async / prompt A/B / 자동 promotion | MVP/Phase 11+ |

## 핵심 원칙: proposal-first + 런타임 0 (★)

- meta_factory는 **자동 적용 도구가 아니라 proposal-first 도구**. 생성 결과는 `meta_factory/outputs/generated_harnesses/` 또는 `meta/proposals/`에 먼저 둔다.
- 생성된 harness는 validation_workflow 통과 전 active로 간주하지 않는다.
- ★ FastAPI/Next.js/Supabase 런타임 변경 **0줄** (A9 — 회귀 검증의 핵심 게이트).
- harness-factory Skill은 **proposal-only** — 기존 AGENTS/CLAUDE/PROJECT_STATE/contracts/Skill 직접 수정 금지.

## harness-factory Skill 키워드 scoping (★ 충돌 회피)

**허용 키워드** (scoped): `harness blueprint, meta_factory, harness scaffold, 도메인 하네스 생성, harness-factory, agent/skill scaffold 설계`
**금지 키워드** (타 Skill 소유 — 충돌):
- `하네스 개선` / `메타 개선` / `회고` → **meta-retrospective** 소유
- bare `하네스 감사` / `구조 점검` / `전체 검토` → **harness-audit** 소유
- `phase 생성` 단독 → phase-start (planning-phase-create 흡수)

→ 우선순위: `harness-audit > harness-factory`, `contract-change > harness-factory`, `eval-run > harness-factory validation`

## 단어 수준 금지 (신규 파일)
- `자동 생성기 구현`, `generator 코드` (NG11 — 설계/skeleton 참조는 허용)
- `자동 반영`, `자동 active 전환` (NG10 — 금지 명시는 허용)
- `Anthropic`, `Spring`, `Expo`, `자동 편집`, `TTS`, `BGM`

## 회피 패턴
- ❌ "factory 김에 자동 generator도" → NG11
- ❌ "blueprint 김에 기존 contract 정리도" → NG7
- ❌ "Skill 김에 AGENTS/CLAUDE 라우터도 갱신" → NG6/NG7
- ❌ runtime 파일 1줄이라도 변경 → NG1~NG3 (A9 위반)
