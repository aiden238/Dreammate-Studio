# Proposal — Phase M0 Slice 3 harness-factory Skill 등록 (#21, proposal-only)

> 작성일: 2026-05-31
> 작성자: Claude (Phase M0 Slice 3 sub-agent)
> 유형: Skill 신규 등록 (Skill 도 contract 처럼 취급 — INDEX §사용 원칙 4 + Skill 신규/변경 절차)
> 결정 근거: ADR-035 (L3 Meta-Factory 도입 — harness-factory 키워드 scoping)
> contract-change 로그: CC-006 (`docs/contract_changes/2026-05-31_phase-M0-skill-index.md`)
> ★ 런타임 변경 0 (A9) — 문서 레이어. proposal-only Skill.

---

## 1. 제안 요약

L3 Meta-Harness Factory(`harness/meta_factory/`)의 진입점 Skill `harness-factory` 를 신규 등록한다 (#21). domain_brief → harness blueprint 초안 생성 + agent·skill·contract·eval scaffold 제안 + 기존 하네스 충돌 분석을 담당한다. ★ **proposal-only** — 생성물은 `meta_factory/outputs/` 또는 `meta/proposals/` 에 먼저 두고, validation_workflow 6 검증 + 사용자 승인 전까지 active 로 간주하지 않는다.

## 2. 무엇을 (변경)

- `.claude/skills/harness-factory/SKILL.md` 신규 (frontmatter + 본문 — 트리거 / 절차 5단계 / 허용·금지 / 사용하지 않는 경우 / 우선순위 / 변경 이력).
- `.claude/skills/INDEX.md` 수정 — 헤더 20→21 + Meta-Factory 1개 섹션(#21) + 우선순위 표 3 관계 + 키워드 충돌 검토 섹션(충돌 0).

## 3. 왜 (기대 효과)

- L3 Meta-Factory(Slice 1~2 — README/factory_contract/schema/workflow/templates/blueprint)의 **Skill 진입점** 확보 → 키워드 자동 트리거로 generation/validation 절차 진입.
- self_improvement_loop + harness-audit + meta-retrospective 문화의 **자연 확장** (L2 in-place 개선 ↔ L3 하네스 생성·blueprint 책임 분리).
- 즉시 가치: 현재 하네스 blueprint(온보딩/감사 문서) 진입 + 메타 문화 정식화. 생성 payoff 는 2nd 하네스 착수 시점까지 이연 (payoff deferred — ADR-035).

## 4. 어디에 (대상)

- `.claude/skills/harness-factory/SKILL.md` (신규) + `.claude/skills/INDEX.md` (등록).
- 데이터/절차는 `meta_factory/` (README / factory_contract / generation_workflow / validation_workflow / templates / blueprints / outputs) 에 둠 (Skill 본문은 절차만 — INDEX §사용 원칙 3).

## 5. 키워드 scoping (★ 충돌 검토)

| 허용 키워드 (scoped) | 금지 키워드 (타 Skill 소유) |
|---|---|
| `하네스 blueprint` / `meta_factory` / `harness scaffold` / `도메인 하네스 생성` / `agent/skill scaffold 설계` / `harness-factory` | `하네스 개선`/`메타 개선`/`회고`(meta-retrospective) · bare `하네스 감사`/`구조 점검`/`전체 검토`(harness-audit) · `phase 생성` 단독(phase-start) |

- 충돌 검토 결과 (harness-audit §3 절차): 기존 20 Skill description 키워드와 **충돌 0** (INDEX §키워드 충돌 검토 표).
- 동시 매칭 가능 3 Skill 우선순위: `harness-audit > harness-factory`, `contract-change > harness-factory`, `eval-run > harness-factory (validation)`.

## 6. 영향 / 위험

- **영향**: INDEX 1 섹션 + 우선순위 3 관계 + SKILL.md 1 신규. 기존 20 Skill 본문 0줄.
- **위험**: harness-factory 가 generated harness 를 자동 active 전환 → ★ proposal-only 로 차단 (factory_contract 규칙 7). 기존 하네스 직접 수정 → 금지 명시 + contract-change 경유 (규칙 2/4/5).
- **런타임 위험**: 0 (A9 — 문서 레이어, backend/apps/migrations 0줄).

## 7. 우선순위

- **보통** — meta-phase 산출물 (즉시 가치 = blueprint 진입점, 생성 payoff deferred). proposal-only Skill 이므로 실 트리거는 2nd 하네스 또는 generated harness 생성 시점.

## 8. 검토 / 승인 절차 (Skill 도 contract 처럼 취급)

```
1. ✅ contract-change SKILL 절차 (Skill 도 contract 처럼 취급 — INDEX §사용 원칙 4)
2. ✅ meta/proposals/ 변경 제안서 작성 (본 문서)
3. ✅ description 키워드 충돌 검토 (INDEX.md 표 갱신 — 충돌 0)
4. ✅ 승인 후 SKILL.md 작성 (ADR-035 선행 승인 기반)
5. ✅ 변경 로그를 SKILL.md frontmatter version v1.0.0 + CC-006 에 반영
6. → harness-audit 다음 회차에 키워드 충돌 / 깨진 참조 재확인 (Phase 10+)
```

## 9. 다음 액션

- [x] harness-factory/SKILL.md 작성 (proposal-only, 키워드 scoped)
- [x] INDEX.md #21 등록 + 우선순위 + 키워드 충돌 검토
- [x] CC-006 (`docs/contract_changes/2026-05-31_phase-M0-skill-index.md`)
- [ ] (Phase 10+) harness-factory dry-run / trigger validation 샘플 / with-without 비교 샘플 — generated harness 첫 생성 시점
