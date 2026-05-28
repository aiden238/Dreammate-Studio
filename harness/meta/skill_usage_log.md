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
> Phase 4.5 entry 갱신: 2026-05-28 (Slice 1 sub-agent)
> Phase 4.5 종료 갱신: 2026-05-28 (Slice 4)
> Phase 6 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 6 종료 갱신: 2026-05-29 (Slice 4)
> Phase 5 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 5 종료 갱신: 2026-05-29 (Slice 5 sub-agent)
> Phase 5.5 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 5.5 종료 갱신: 2026-05-29 (Slice 4)

| Skill | 첫 트리거 | 마지막 트리거 | 누적 | 최근 30일 | 상태 | 비고 |
|---|---|---|---|---|---|---|
| phase-start | 2026-05-26 | 2026-05-29 | 8 | 8 | active | v1.0.0 → v1.1.0 → v1.2.0 (P2) → v1.3.0 (P-X1 §6.3 §SELF-VERIFICATION). Phase 1+2+3+4+4.5+6+5+5.5 진입 (Phase 5.5 entry Slice 1 트리거 — Slice 1에서 누적 8 진행) |
| qa-check | 2026-05-26 | 2026-05-29 | 32 | 32 | active | v1.1.0 → v1.2.0 (P3, 카테고리 11). Phase 1:8 + Phase 2:7 + Phase 3:6 + Phase 4:5 + Phase 4.5:1 + Phase 6:2 + Phase 5:2 + **Phase 5.5:1 (Slice 4 final)** |
| contract-change | 2026-05-26 | 2026-05-29 | 5 | 5 | active | CC-001 (Option B) + P1~P4 Skill 갱신 + P-X1 phase-start v1.3.0 + **Phase 6 Slice 2 첫 본격 실 변경 ★** (output_schema §9 canonical + §10 Body + agent_io_contract §6 Rewriter v1.1.0 + api_contract §8.3 + ADR-018/019) + **Phase 5 Slice 2 두 번째 본격 ★** (`db_schema.md` 신규 — DB schema 첫 정식 contract + 4계층 + plans + users + JSONB 컬럼). 회귀 0 유지. Phase 3+4+4.5+5.5는 contract 변경 0 (Phase 5.5는 ADR-023/024 신규만, contracts 직접 변경 없음) |
| meta-retrospective | 2026-05-26 | 2026-05-29 | 8 | 8 | active | Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 4.5 + Phase 6 + Phase 5 + **Phase 5.5 (지금)** 회고 |
| phase-complete | 2026-05-26 | 2026-05-29 | 8 | 8 | active | v1.0.0 → v1.1.0 (P4 §1.5 smoke test) → v1.2.0 (P-X2 §1.6 변경성 시뮬 자동 게이트, Phase 4.5 entry 도입). Phase 1+2+3+4+4.5+6+5+5.5 종료. Phase 4.5 Slice 4 v1.2.0 §1.6 첫 자동 게이트 (5/5) + Phase 6 Slice 4 두 번째 (5/5) + Phase 5 Slice 5 세 번째 자동 게이트 (scenario_simulation v2 10/10 PASS) + **Phase 5.5 Slice 4 네 번째 자동 게이트 (scenario_simulation v2 10/10 PASS)** ★ |
| harness-audit | 2026-05-27 | 2026-05-29 | 5 | 5 | active | audit_naming + audit_page_component 모두 자동 호출 (Phase 4 D-1 정규화 보강 + Phase 4.5 Slice 1+4 + Phase 6 Slice 1+4 + Phase 5 Slice 1+5 + **Phase 5.5 Slice 4**) — 수동 Skill 호출 0. Phase 5.5 Slice 4 audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 유지, phase-complete v1.2.0 §1.6 허용) |
| design-review | 2026-05-27 | 2026-05-29 | 6 | 6 | active | Phase 2 Slice 6 (spec-only 첫) + Phase 3 Slice 6 (impl 두 번째 §B) + Phase 4 Slice 4 (impl 세 번째 §B) + Phase 4.5 Slice 4 (impl 네 번째 §B) + Phase 6 Slice 4 (impl 다섯 번째 §B) + **Phase 5 Slice 5 (impl 여섯 번째 §B, PlanCard 17연속 무수정 정합)** |
| multi-llm-validation | 2026-05-28 | 2026-05-29 | 4 (1 informal + 3 formal) | 4 | active | Phase 4 informal GPT 검토 + Phase 4.5 entry formal self V1~V4 PASS (외부 placeholder 분리) + Phase 6 entry formal self 두 번째 V1~V5 PASS + **Phase 5 entry formal self ★ 세 번째** V1~V6 PASS (Supabase 채택 / JWT / RLS / SSE / revise_history JSONB / canonical DB). **P-VALIDATION-FORMAL-001 정식 패턴 확정 (3회 누적)** |
| **agent-io-check** | **2026-05-29** | **2026-05-29** | **2** | 2 | **active** | Phase 6 Slice 4 첫 정식 트리거 (Rewriter v1.1.0 + Critic canonical 정합 PASS) + **Phase 5 Slice 5 두 번째 회귀 검증** (Phase 6 baseline 유지 PASS — Phase 5는 agents 변경 0이므로 회귀만 검증) |
| eval-design | - | - | 0 | 0 | unused | failure_cases.md 작성은 INDEX + ADR로 처리 (skill 미사용) |
| eval-run | - | - | 0 | 0 | unused | Phase 9+ Critic revise effect eval / fallback 완전 제거 시 활성화 |
| rag-design | - | - | 0 | 0 | unused | Phase 7 RAG 본격화 시 활성화 |
| rag-update | - | - | 0 | 0 | unused | Phase 7+ |
| prompt-version-review | - | - | 0 | 0 | unused | Phase 7+ prompt_registry P-007/P-008 정식화 시 (NG8 Phase 6 defer) |
| ai-architecture-review | - | - | 0 | 0 | unused | Phase 7/8 진입 시 활성화 |
| context-compact | - | - | 0 | 0 | unused | Phase 1~6 컨텍스트 충분 |
| phase-review | - | - | 0 | 0 | unused | Phase 중간 health check 시 활성화 |
| bug-triage | - | - | 0 | 0 | unused | 버그 발견 시 활성화 |
| **security-review** | **2026-05-29** | **2026-05-29** | **2 ★ 첫 정식 + 두 번째 final** | 2 | **active** | **Phase 5 Slice 1 entry 첫 정식 트리거** — T1~T6 위협 모델 + §4 영역 1~10 점검. **Phase 5 Slice 5 final 두 번째 트리거** — Slice 2~4 실 구현 verify (T1 httpOnly cookie PASS / T2 RLS 0003 PASS / T4 Origin 검증 PASS) + 영역 1~10 6 PASS + 2 PARTIAL + 2 N/A. **P-SECURITY-REVIEW-001 신규 후보 (2-trigger 패턴)** |
| cost-review | - | - | 0 | 0 | unused | Phase 9+ 비용 본격 추적 시 |

**Phase 1 사용 요약**: 4 Skill 활용 (phase-start + qa-check 8회 + contract-change + meta-retrospective). 16 Skill은 아직 unused.

**Phase 2 사용 요약**: 6 Skill 활용 (phase-start + qa-check 7회 + meta-retrospective + phase-complete + harness-audit + ★ design-review 첫 사용). Phase 1 누적 + Phase 2 = 7 Skill 활성화, 13 unused.

**Phase 3 사용 요약**: 7 Skill 활용 (phase-start v1.3.0 + qa-check 6회 + contract-change (P-X1 적용) + meta-retrospective + phase-complete + harness-audit (audit_page_component.ps1 신규) + design-review 두 번째 사용 — impl 절차 §B). Phase 1~3 누적 = 7 Skill 활성화, 13 unused.

**Phase 4 사용 요약**: 7 Skill 활용 (phase-start v1.3.0 + qa-check 5회 + meta-retrospective + phase-complete + harness-audit + design-review 세 번째 — impl §B + ★ multi-llm-validation 첫 사용 — informal GPT 검토). Phase 1~4 누적 = 8 Skill 활성화, 12 unused. **multi-llm-validation 첫 informal 트리거 — Phase 5+ 정식 호출 권장**.

**Phase 4.5 사용 요약**: 7 Skill 활용 (phase-start v1.3.0 + qa-check + meta-retrospective + phase-complete v1.2.0 ★ + harness-audit + design-review 네 번째 사용 + multi-llm-validation **formal** ★ 첫 정식 트리거). Phase 1~4.5 누적 = 9 Skill 활성화, 11 unused. **multi-llm-validation formal + P-X2 자동 게이트** 첫 트리거.

**Phase 6 사용 요약**: 9 Skill 활용 (phase-start v1.3.0 + qa-check + contract-change ★ 본격 + multi-llm-validation formal 두 번째 + agent-io-check ★ 첫 정식 + harness-audit + design-review + meta-retrospective + phase-complete v1.2.0 두 번째). Phase 1~6 누적 = 10 Skill active, 10 unused. **agent-io-check + contract-change 본격 트리거** (Phase 5 진입 전 baseline 완성).

**Phase 5 사용 요약**: 11 Skill 활용 (phase-start v1.3.0 + qa-check + contract-change (db_schema.md, Slice 2) + multi-llm-validation **formal 세 번째 (Slice 1)** + **security-review ★ 첫 정식 + 두 번째 final** (Slice 1 + Slice 5) + agent-io-check 두 번째 회귀 (Slice 5) + harness-audit (Slice 1+5) + design-review (Slice 5) + meta-retrospective (Slice 5) + phase-complete v1.2.0 세 번째 (Slice 5)). Phase 1~5 누적 = **12 Skill 활성화**, 8 unused. **security-review + contract-change 본격 안정화**.

**Phase 5 Slice 5 종료 갱신**: 7 Skill 추가 활용 (Slice 1 4 + Slice 5 7 = 누적 11) — contract-change 두 번째 + security-review 두 번째 final + agent-io-check 회귀 + harness-audit + design-review + meta-retrospective + phase-complete v1.2.0 세 번째. Phase 5 종료 의무 완료.

**Phase 5.5 사용 요약**: 5 Skill 활용 (phase-start v1.3.0 + qa-check + harness-audit + meta-retrospective + phase-complete v1.2.0 네 번째). Phase 1~5.5 누적 = **12 Skill 활성화**, 8 unused.

이번 Slice 미사용 Skill (의도된):
- contract-change (ADR만 신규, contract 직접 변경 없음)
- security-review (Phase 5에서 완료, 보안 변경 없음)
- agent-io-check (agents/* 변경 없음)
- design-review (frontend 변경 없음)
- multi-llm-validation (Phase 4.5/6/5에서 형식 정착, Phase 5.5는 강화 작업이므로 형식 재사용)

**Phase 7 진입 시 활성 예상 Skill**: phase-start + qa-check + multi-llm-validation formal 네 번째 + **rag-design ★ 첫 정식** + rag-update + contract-change (rag_data_contract.md) + harness-audit + meta-retrospective + phase-complete.

> Phase 6 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 6 종료 갱신: 2026-05-29 (Slice 4)
> Phase 5 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 5 종료 갱신: 2026-05-29 (Slice 5 sub-agent)
> Phase 5.5 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 5.5 종료 갱신: 2026-05-29 (Slice 4)
