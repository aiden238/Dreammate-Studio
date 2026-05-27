# Phase 2 — Dependencies

---

## 이전 Phase 의존성

| Phase | 이름 | 상태 | 필요 이유 |
|---|---|---|---|
| **Phase 0** | 하네스 초기화 | ✅ done (2026-05-26) | design.md / page_map / component_map / frontend_design_contract baseline |
| **Phase 1** | MVP 기본 플로우 | ✅ done (2026-05-26) | PlanCard (기존 활용) / API envelope 형식 / 4 Skill v1.1.0~v1.2.0 강화 |

확인 방법:
- `phases/archive/phase-0-migration/acceptance.md` → 11/11 [x]
- `phases/archive/phase-1-mvp-basic-flow/acceptance.md` → 8/8 implementation
- `PROJECT_STATE.md` → `phase_2_status: pending_entry` → entry 후 active

---

## 외부 의존성 (Phase 2는 frontend spec only)

| 서비스 | 용도 | Phase 2 사용 여부 |
|---|---|---|
| OpenAI API | LLM | ❌ Phase 2는 spec만, 호출 없음 |
| Supabase | DB | ❌ Phase 2는 spec만 |
| pgvector | RAG | ❌ Phase 2는 spec만 |

→ **Phase 2는 외부 서비스 무의존**. 작업 환경 = 마크다운 + ASCII art만.

---

## 도구 의존성

| 도구 | 용도 | Phase 2 |
|---|---|---|
| PowerShell 5.1 | sanity / audit_naming | 필요 |
| Git | commit / push | 필요 |
| Markdown viewer | 작업 결과 검증 | 권장 (선택) |

기존 Phase 1 환경 그대로 사용 가능. 신규 install 0.

---

## 코드 의존성

Phase 2는 코드 무변경 → npm / pip install 0.

Phase 1에서 install된 패키지 그대로 유지:
- backend/fastapi: fastapi 0.115 / pytest 8.3 / openai 1.51 / pydantic 2.9 / supabase 2.7 등
- apps/web: next 14 / react 18 / typescript / tailwindcss

---

## 관련 Contracts (읽어야 할 문서)

Phase 2 작업 시 필수 참조:

| 문서 | 이유 |
|---|---|
| `apps/web/design.md` (Phase 0) | 핵심 UX 규칙 baseline (보강 대상) |
| `apps/web/page_map.md` (Phase 0) | 기존 page 구조 (확장 대상) |
| `apps/web/component_map.md` (Phase 0) | 기존 컴포넌트 (확장 대상) |
| `docs/contracts/frontend_design_contract.md` | 디자인 contract (보강 가능, 큰 변경은 contract-change) |
| `ai_system/prompts/prompt_registry.md` | P-001~P-007 매핑 (Discovery 7-step과 1:1) |
| `docs/contracts/output_schema.md` | P-XXX 출력 구조 (TS interface 매핑 참조) |
| `docs/contracts/api_contract.md` §8 | wizard endpoint 명세 (Phase 4 migration 대상) |
| `eval/golden_set.md` (Phase 0/1) | UX 흐름 검증 케이스 |
| `eval/failure_cases.md` (Phase 1) | 차단 UX 패턴 참조 |
| `meta/proposals/2026-05-26_phase-1-retrospective-proposals.md` | P1~P4 적용 완료 baseline |

---

## Skill 의존성

Phase 2 동안 사용 예상:

| Skill | 사용 시점 | 횟수 예상 |
|---|---|---|
| `phase-start` (v1.2.0) | Phase 2 진입 (이미 진행 중) | 1 |
| `contract-change` | frontend_design_contract 보강 시 (선택) | 0~1 |
| `design-review` | Slice 6 | 1 (첫 사용) |
| `qa-check` (v1.2.0) | 매 Slice + 최종 | 7 |
| `meta-retrospective` | Slice 6 | 1 |
| `phase-complete` (v1.1.0) | Phase 종료 | 1 |
| `harness-audit` (v1.1.0) | 필요 시 (선택) | 0~1 |
| `multi-llm-validation` | non_goals 변경 제안 시 (없을 가능성 높음) | 0 |

`design-review` Skill 첫 사용 — 절차 부재 발견 시 P-X 회고 proposal 등록.

---

## Phase 2 → Phase 3 인수 항목 (deferred 명시)

Phase 2가 의도적으로 안 하는 것 = Phase 3가 인수:

```
1. Step 2~7 wireframe 상세 (Phase 3에서 코드 작성 중 도출)
2. QuickInputCard variants (Phase 3 alt 발생 시)
3. PlanCard 4-layer 회고 정합 (Phase 3 코드 작성 후)
4. PlanComparisonCard (Phase 4 진입 시)
5. audit_page_component.ps1 (Phase 3 실 파일 생긴 후)
```

→ Phase 2 closing_notes에 위 5개 명시.

---

## 주의사항

- Phase 2는 spec phase — Phase 3 진입 시 spec 100% 따라가게 작성
- design_handoff.md가 가장 중요한 산출물 (Phase 11+ 디자인 변경 시 가이드)
- 모든 변경은 audit_naming + design-review 통과해야 phase-complete
- Step 5 Tone form 패턴은 의도된 예외 — 5-card 일관 위반 아님
