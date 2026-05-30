# Contract Change Log — Phase M0 Slice 3 INDEX Skill 등록 (harness-factory #21)

> ID: CC-006
> Status: **decided + applied** (2026-05-31, Phase M0 Slice 3, ★ meta-phase)
> Date: 2026-05-31
> Decision: harness-factory Skill (proposal-only, 키워드 scoped) #21 INDEX 등록 — ADR-035 선행 승인 기반
> Author: Claude (Phase M0 Slice 3 sub-agent)
> Related contracts: `.claude/skills/INDEX.md` (Skill 도 contract 처럼 취급 — INDEX §사용 원칙 4 + Skill 신규/변경 절차), `harness/.claude/skills/harness-factory/SKILL.md` (신규)
> Related ADR: ADR-035 (`docs/decisions/phase_M0_meta_factory.md` — L3 Meta-Factory 도입 + harness-factory 키워드 scoping)
> Proposal: `meta/proposals/2026-05-31_phase-M0-harness-factory-skill.md`
> Skill: contract-change (절차 — Skill 도 contract 처럼 취급) + harness-audit (§3 키워드 충돌 검토)
> ★ 런타임 변경 0 (A9) — INDEX.md + SKILL.md 문서 레이어. backend/apps/migrations 0줄.

---

## 1. 변경 요약

| 대상 | 변경 |
|---|---|
| `.claude/skills/INDEX.md` | 헤더 "총 20개 → 21개 (절차 핵심 14 + 검토/감사 6 + **Meta-Factory 1**)". Skill 목록에 **Meta-Factory 1개** 섹션 추가 (#21 harness-factory). 우선순위 충돌 해결 표에 3 관계 추가 (harness-audit > harness-factory, contract-change > harness-factory, eval-run > harness-factory). **키워드 충돌 검토** 섹션 신규 (충돌 0 기록). |
| `.claude/skills/harness-factory/SKILL.md` | 신규 (proposal-only, 키워드 scoped). frontmatter(name/description scoped/applies_to [claude]/phase [phase-10, ongoing]/version v1.0.0) + 본문(트리거 / 절차 5단계 / 허용·금지 8 규칙 정합 / 사용하지 않는 경우 라우팅 / 우선순위 / 변경 이력). |

## 2. 코드 영향 (런타임 0 — A9)

```
backend/fastapi/**  — 0줄 (A9)
apps/web/**         — 0줄 (PlanCard.tsx / component_map.md 0줄)
db/migrations/**    — 0줄 (A9)
```

> Skill 등록은 문서 레이어 변경 — 런타임 무관 (factory_contract 규칙 1). 기존 20 Skill SKILL.md 본문 변경 0 (harness-factory 외).

## 3. 회귀 안전 근거

- **proposal-only** — harness-factory 는 generated harness 를 자동 active 전환하지 않음 (factory_contract 규칙 7). 기존 AGENTS/CLAUDE/PROJECT_STATE/contracts/Skill 직접 수정 금지 (규칙 2/4/5/6).
- **키워드 scoped — 충돌 0** — description 키워드(하네스 blueprint / meta_factory / harness scaffold / 도메인 하네스 생성)가 기존 20 Skill 의 description 키워드와 비중첩 (INDEX §사용 원칙 5). harness-audit("감사/점검") / meta-retrospective("개선/회고") / phase-start("phase 시작")와 의미 명확 구분.
- **우선순위 표 편입** — 동시 매칭 가능 3 Skill 에 우선순위 관계 추가 (harness-audit / contract-change / eval-run 상위). 라우터 충돌 0.
- **트리거 0 (proposal-only Skill)** — 등록만, 실 트리거는 2nd 하네스 착수 또는 generated harness 생성 시점 (payoff deferred — ADR-035).
- pytest 339 / P-X1 47 / PlanCard 35 / component_map 45 baseline 불변 (런타임 무관).

## 4. 검증 결과

```
INDEX.md: 총 21개 (헤더 + Meta-Factory 섹션 + 우선순위 3 관계 + 키워드 충돌 검토 0).
harness-factory/SKILL.md: 신규 (proposal-only, 키워드 scoped).
harness-audit §3 키워드 충돌 검토: harness-audit/meta-retrospective/phase-start/contract-change/eval-run ↔ harness-factory 충돌 0.
scenario_simulation v7: SM2 (harness-factory Skill + INDEX) PASS.
smoke_test_phase_M0: Step 5 (harness-factory Skill 존재 + INDEX #21 등록) PASS.
★ git diff: backend/fastapi / apps/web / db/migrations 0줄 (A9). 기존 .claude/skills/* (harness-factory 외) 0줄.
```

## 5. Rollback

- 문서 변경은 git revert. INDEX.md 헤더/섹션/우선순위/충돌 검토 복원 + harness-factory/ 폴더 제거 시 회귀 0 (proposal-only, 트리거 0).

## 6. 변경 이력

- 2026-05-31: 제안서 작성(meta/proposals) + ADR-035 선행 승인 기반 + INDEX #21 등록 + harness-factory/SKILL.md 신규 + harness-audit §3 키워드 충돌 검토(충돌 0) + 검증 (Phase M0 Slice 3). **P-CONTRACT-FIRST-001 정신 — Skill 도 contract 처럼 취급 (INDEX §Skill 신규/변경 절차).**
