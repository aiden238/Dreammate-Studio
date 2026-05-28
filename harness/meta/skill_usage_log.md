# meta/skill_usage_log.md

> 🚧 Placeholder (Phase 0 진입 직후 생성. 첫 Skill 트리거부터 자동 누적 시작)

## 목적

각 Skill의 실제 트리거 빈도를 추적한다.
- 6개월 이상 트리거되지 않은 Skill → 폐기 후보
- 한 세션에서 3회 이상 트리거된 Skill → 자동화 후보 (스크립트화 검토)

## 자동 갱신 주체

- `phase-complete` Skill이 Phase 종료 시 갱신
- `meta-retrospective` Skill이 회고 시 검토

## 항목 형식

```markdown
| Skill | 첫 트리거 | 마지막 트리거 | 누적 트리거 수 | 최근 30일 | 상태 |
|---|---|---|---|---|---|
| phase-start | 2026-05-24 | 2026-05-24 | 1 | 1 | active |
| contract-change | - | - | 0 | 0 | unused |
```

## 상태 분류

- `active`: 최근 30일 내 트리거됨
- `unused`: 한 번도 트리거 안 됨
- `dormant`: 90일 이상 트리거 안 됨
- `deprecated`: 폐기 결정됨

## 인덱스

> 누적 시작: 2026-05-26 (Phase 1 완료 시점)
> Phase 2 갱신: 2026-05-27 (Phase 2 종료 시점)
> Phase 3 갱신: 2026-05-28 (Phase 3 종료 시점)
> Phase 4 갱신: 2026-05-28 (Phase 4 종료 시점)

| Skill | 첫 트리거 | 마지막 트리거 | 누적 | 최근 30일 | 상태 | 비고 |
|---|---|---|---|---|---|---|
| phase-start | 2026-05-26 | 2026-05-28 | 4 | 4 | active | v1.0.0 → v1.1.0 → v1.2.0 (P2) → v1.3.0 (P-X1 §6.3 §SELF-VERIFICATION). Phase 1+2+3+4 진입 |
| qa-check | 2026-05-26 | 2026-05-28 | 26 | 26 | active | v1.1.0 → v1.2.0 (P3, 카테고리 11). Phase 1:8 + Phase 2:7 + Phase 3:6 + Phase 4:5 (entry + Slice 1~3 + final) |
| contract-change | 2026-05-26 | 2026-05-28 | 3 | 3 | active | CC-001 (Option B) + P1~P4 Skill 갱신 + P-X1 phase-start v1.3.0. Phase 3+4는 contract 변경 0 (Phase 4 ADR-014/015는 decisions/이며 contract 직접 변경은 아님) |
| meta-retrospective | 2026-05-26 | 2026-05-28 | 4 | 4 | active | Phase 1 + Phase 2 + Phase 3 + Phase 4 회고 |
| phase-complete | 2026-05-26 | 2026-05-28 | 4 | 4 | active | v1.0.0 → v1.1.0 (P4 §1.5 smoke test). Phase 1+2+3+4 종료. Phase 4는 smoke_test_phase_4.ps1 자동 호출 (8/8 PASS) |
| harness-audit | 2026-05-27 | 2026-05-28 | 1 | 1 | active | audit_naming + audit_page_component 모두 자동 호출 (Phase 4는 audit_page_component.ps1 D-1 정규화 보강) — 수동 Skill 호출 0 (Phase 1~4) |
| design-review | 2026-05-27 | 2026-05-28 | 3 | 3 | active | Phase 2 Slice 6 (spec-only 첫 사용) + Phase 3 Slice 6 (impl phase 두 번째 — §B) + Phase 4 Slice 4 (impl phase 세 번째 — §B, PlanCard 무수정 정합) |
| multi-llm-validation | 2026-05-28 | 2026-05-28 | 1 (informal) | 1 | active (Phase 5+ formal 권장) | Phase 4 진입 전 GPT 검토 (사용자 외부 진행) — 정식 Skill 호출 X, 결과 채택 명확. Phase 5+ 진입 전 정식 호출 권장 (meta/validations/ 누적) |
| eval-design | - | - | 0 | 0 | unused | failure_cases.md 작성은 INDEX + ADR로 처리 (skill 미사용) |
| eval-run | - | - | 0 | 0 | unused | Phase 4.5+ Critic revise 도입 시 활성화 |
| rag-design | - | - | 0 | 0 | unused | Phase 7 RAG 본격화 시 활성화 |
| rag-update | - | - | 0 | 0 | unused | Phase 7+ |
| prompt-version-review | - | - | 0 | 0 | unused | prompt_registry 변경 시 활성화 |
| ai-architecture-review | - | - | 0 | 0 | unused | Phase 7/8 진입 시 활성화 |
| context-compact | - | - | 0 | 0 | unused | Phase 1~4 컨텍스트 충분 |
| phase-review | - | - | 0 | 0 | unused | Phase 중간 health check 시 활성화 |
| agent-io-check | - | - | 0 | 0 | unused | Phase 4.5+ Rewriter 도입 시 활성화 (Phase 4는 agent contract 변경 0) |
| bug-triage | - | - | 0 | 0 | unused | 버그 발견 시 활성화 |
| security-review | - | - | 0 | 0 | unused | Phase 5+ Auth/RLS 도입 시 또는 보안 인시던트 시 |
| cost-review | - | - | 0 | 0 | unused | Phase 9+ 비용 본격 추적 시 |

**Phase 1 사용 요약**: 4 Skill 활용 (phase-start + qa-check 8회 + contract-change + meta-retrospective). 16 Skill은 아직 unused.

**Phase 2 사용 요약**: 6 Skill 활용 (phase-start + qa-check 7회 + meta-retrospective + phase-complete + harness-audit + ★ design-review 첫 사용). Phase 1 누적 + Phase 2 = 7 Skill 활성화, 13 unused.

**Phase 3 사용 요약**: 7 Skill 활용 (phase-start v1.3.0 + qa-check 6회 + contract-change (P-X1 적용) + meta-retrospective + phase-complete + harness-audit (audit_page_component.ps1 신규) + design-review 두 번째 사용 — impl 절차 §B). Phase 1~3 누적 = 7 Skill 활성화, 13 unused.

**Phase 4 사용 요약**: 7 Skill 활용 (phase-start v1.3.0 + qa-check 5회 + meta-retrospective + phase-complete + harness-audit + design-review 세 번째 — impl §B + ★ multi-llm-validation 첫 사용 — informal GPT 검토). Phase 1~4 누적 = 8 Skill 활성화, 12 unused. **multi-llm-validation 첫 informal 트리거 — Phase 5+ 정식 호출 권장**.

**Phase 5 진입 시 활성 예상 Skill**: phase-start v1.3.0 (유지) + qa-check (DB/Auth phase는 카테고리 1/2/3/5/9/11 활성) + contract-change (Supabase 스키마 도입) + multi-llm-validation **formal** (Phase 5는 큰 phase, DB/Auth 설계 검증 필요) + agent-io-check (Phase 4.5+ Rewriter 도입 시) + security-review (Auth/RLS 도입 시).
