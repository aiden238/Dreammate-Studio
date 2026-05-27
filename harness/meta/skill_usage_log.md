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

| Skill | 첫 트리거 | 마지막 트리거 | 누적 | 최근 30일 | 상태 | 비고 |
|---|---|---|---|---|---|---|
| phase-start | 2026-05-26 | 2026-05-26 | 1 | 1 | active | v1.0.0 → v1.1.0 → v1.2.0 (P2 적용) |
| qa-check | 2026-05-26 | 2026-05-26 | 8 | 8 | active | v1.1.0 → v1.2.0 (P3 적용, 카테고리 11 Contract Drift) |
| contract-change | 2026-05-26 | 2026-05-27 | 2 | 2 | active | CC-001 (Option B) + P1~P4 Skill 갱신 |
| meta-retrospective | 2026-05-26 | 2026-05-26 | 1 | 1 | active | phase-1.md 작성 |
| phase-complete | 2026-05-26 | 2026-05-26 | 1 | 1 | active | v1.0.0 → v1.1.0 (P4 적용, §1.5 자동 smoke test) |
| harness-audit | 2026-05-27 | 2026-05-27 | 1 | 1 | active | v1.0.0 → v1.1.0 (P1 적용, §6.5 audit_naming) — audit_naming.ps1 첫 실행 0 drift |
| design-review | - | - | 0 | 0 | unused | Phase 2 진입 시 활성화 |
| eval-design | - | - | 0 | 0 | unused | failure_cases.md 작성은 INDEX + ADR로 처리 (skill 미사용) |
| eval-run | - | - | 0 | 0 | unused | Phase 4+ Critic revise 도입 시 활성화 |
| rag-design | - | - | 0 | 0 | unused | Phase 7 RAG 본격화 시 활성화 |
| rag-update | - | - | 0 | 0 | unused | Phase 7+ |
| prompt-version-review | - | - | 0 | 0 | unused | prompt_registry 변경 시 활성화 |
| ai-architecture-review | - | - | 0 | 0 | unused | Phase 7/8 진입 시 활성화 |
| multi-llm-validation | - | - | 0 | 0 | unused | 큰 결정 발생 시 활성화 |
| context-compact | - | - | 0 | 0 | unused | (이번 세션은 컨텍스트 충분) |
| phase-review | - | - | 0 | 0 | unused | Phase 중간 health check 시 활성화 |
| agent-io-check | - | - | 0 | 0 | unused | Phase 4+ agent 추가 시 활성화 |
| bug-triage | - | - | 0 | 0 | unused | 버그 발견 시 활성화 |
| security-review | - | - | 0 | 0 | unused | Phase 6+ 또는 보안 인시던트 시 |
| cost-review | - | - | 0 | 0 | unused | Phase 9+ 비용 본격 추적 시 |

**Phase 1 사용 요약**: 4 Skill 활용 (phase-start + qa-check 8회 + contract-change + meta-retrospective). 16 Skill은 아직 unused — Phase 2~10 진행하며 단계적 활성화 예상.
