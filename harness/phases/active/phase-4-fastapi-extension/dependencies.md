# Phase 4 — Dependencies

---

## 이전 Phase 의존성

| Phase | 이름 | 상태 | 필요 이유 |
|---|---|---|---|
| **Phase 0** | 하네스 초기화 | ✅ done (2026-05-26) | contracts / Skill / ai_system baseline |
| **Phase 1** | MVP 기본 플로우 | ✅ done (2026-05-26) | backend FastAPI + Phase 1 `/generate` endpoint (Phase 4에서 호환 유지) + pytest 62 회귀 baseline |
| **Phase 2** | PWA 설계 | ✅ done (2026-05-27) | design_handoff.md 변경성 baseline + component_map.md (read-only) |
| **Phase 3** | Next.js PWA UI | ✅ done (2026-05-28) | frontend baseline + Discovery/Quick routes + P-X1 적용 환경 |

확인:
- `phases/archive/phase-0/1/2/3` 모두 acceptance PASS
- `PROJECT_STATE.md`: 모든 이전 phase completed
- audit_naming 0 drift (Phase 4 진입 시점)
- pytest 62/62 + next build OK

---

## 외부 의존성 (Phase 4는 backend + frontend 모두 변경)

| 서비스 | 용도 | Phase 4 사용 여부 |
|---|---|---|
| OpenAI API | gpt-4o-mini (3-plan generation × 3 parallel) | ✅ 활성 |
| Supabase | DB (Phase 1 graceful skip 유지) | 선택 — 미설정 시 자동 skip |
| pgvector | RAG (Phase 1 fallback 유지) | 선택 — 미설정 시 fallback |

**Multi-model 가능성** (사용자 결정 4-b):
- 향후 Anthropic / Google 등 추가 가능 (Phase 21+ 본격)
- Phase 4 default: `["gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini"]` 또는 `["gpt-4o-mini", "gpt-4o-mini", "gpt-4o"]` (사용자 결정 — Slice 2 dispatch 전)

---

## 도구 의존성

기존 Phase 1~3 도구 그대로 사용:
- PowerShell 5.1 / Python 3.11 / Node.js 18+ / Git / npm

신규 install 0 (Phase 1 requirements.txt + Phase 3 package.json 그대로).

---

## 코드 의존성

신규 install 0. 기존 패키지 활용:
- backend: fastapi 0.115 / openai 1.51 / pydantic 2.9 / pytest 8.3 / supabase 2.7 / psycopg
- frontend: next 14 / react 18 / typescript / tailwindcss / @supabase/supabase-js

**Multi-model 인터페이스용 추가 검토** (향후):
- Anthropic SDK (Phase 21+, Phase 4는 추가 X — 구조만)
- LiteLLM proxy (Phase 21+ 검토)

---

## 관련 Contracts (read-only, 필수 참조)

| 문서 | 이유 |
|---|---|
| `docs/contracts/api_contract.md` §8 | Phase 4 endpoints 정합 (POST /plans/start, /plans/{id}/wizard/{step}, /plans/{id}/generate, GET /plans/{id}) |
| `docs/contracts/output_schema.md` §8 (P-006) | plans length 3 + approach_label enum |
| `docs/contracts/output_schema.md` §9 (P-007 Critic) | 8-dim verdict 구조 (revise loop는 Phase 4.5+) |
| `docs/contracts/agent_io_contract.md` | Planning Agent IO + Critic |
| `docs/contracts/error_response_contract.md` | ErrorEnvelope (Phase 2 Slice 2에서 INV-001 정합 완료) |
| `ai_system/prompts/prompt_registry.md` | P-006 / P-007 프롬프트 (Phase 4 변경 X) |
| `apps/web/page_map.md` | `/plan/{plan_id}` route 명세 |
| `apps/web/component_map.md` ★ | **read-only 절대** (조정 4번) — PlanCard 그대로 활용 |
| `apps/web/design_handoff.md` | 변경성 시뮬 baseline |

---

## Skill 의존성

Phase 4 동안 사용 예상:

| Skill | 사용 시점 | 횟수 예상 |
|---|---|---|
| phase-start v1.3.0 | 진입 (이미 진행 중) | 1 |
| qa-check v1.2.0 | 매 Slice + 최종 | 5 |
| contract-change | (필요 시) page_map.md /plan/[plan_id] 등록 — Slice 4 검토 | 0~1 |
| meta-retrospective | Slice 4 | 1 |
| phase-complete v1.1.0 | Phase 종료 | 1 |
| design-review | (선택) Slice 3 frontend 검토 | 0~1 |
| harness-audit | (선택) | 0 |

---

## Phase 4 → 다음 phase 인수 명세 (사용자 결정 3-c)

Phase 4 종료 시점에 다음 항목 인수:

| ID | 항목 | 다음 phase 처리 |
|---|---|---|
| **D6** (신규) | Critic revise loop + Rewriter (P-008) | Phase 4.5 mini-phase 또는 Phase 6 안 통합 |
| **D7** (신규) | SSE Progress streaming | Phase 5 (Auth/RLS와 함께) |
| **D8** (신규) | PlanComparisonCard 본격 4-layer | Phase 5+ |
| **D3** (Phase 3 → Phase 4 → Phase 5+ 이관 유지) | PlanCard 4-layer 재정의 | Phase 5+ (D4와 함께) |
| **D4** (Phase 3 → Phase 4 → Phase 5+ 이관 유지) | PlanComparisonCard 상세 | Phase 5+ |
| **D2** (Phase 3 → Phase 9 유지) | QuickInputCard alt variants | Phase 9 |
| **Phase 1 endpoint 제거** | 사용자 결정 5-a | Phase 8+ (교차 검토 + 마이그 완료 후) |

---

## 주의사항

- Phase 4는 **GPT 검토 채택 후 축소된 scope** — 새 요청 추가 시 즉시 거절 또는 다음 phase 이관
- component_map.md **11+ 연속 0줄 목표** (Phase 3 7 + Phase 4 4 Slices + Final = 12)
- §SELF-VERIFICATION (P-X1) 4연속 PASS 목표 (Slice 1~4 모두)
- Phase 1 endpoint 무수정 (header만 추가) — 사용자 결정 5-a + 회귀 위험 0
