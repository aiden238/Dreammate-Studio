# Phase 3 — Dependencies

---

## 이전 Phase 의존성

| Phase | 이름 | 상태 | 필요 이유 |
|---|---|---|---|
| Phase 0 | 하네스 초기화 | ✅ done (2026-05-26) | 기본 구조 |
| Phase 1 | MVP 기본 플로우 | ✅ done (2026-05-26) | backend baseline + PlanCard / ErrorCard / ProgressStepper / SubmitButton |
| Phase 2 | PWA 설계 | ✅ done (2026-05-27) | design spec 단일 진실 소스 (17 산출물, read-only) |

확인:
- Phase 1 archive: pytest 62/62 PASS
- Phase 2 archive: 변경성 시뮬레이션 5/5 PASS
- P-X1 적용 완료: phase-start v1.3.0 (commit `3d0b0fb`)

---

## Phase 2 산출물 참조 (read-only)

Phase 3 작업 시 단일 진실 소스로 참조 (수정 금지):

| 문서 | 사용 시점 |
|---|---|
| `apps/web/design_handoff.md` | 모든 Slice (변경성 보장 baseline) |
| `apps/web/component_map.md` | Slice 2/3/4 (컴포넌트 spec) |
| `apps/web/page_map.md` | Slice 5 (routes 매핑) |
| `apps/web/design_system/tokens.md` | Slice 1 (Tailwind 매핑) |
| `apps/web/design_system/component_contract.md` | Slice 2 (4-layer template) |
| `apps/web/design_system/variant_format.md` | Slice 2/3/4 (variants prop 구조) |
| `apps/web/design_system/replaceability_score.md` | Slice 6 (변경성 시뮬레이션) |
| `apps/web/discovery_flow.md` | Slice 2/3 (Step별 prompt 매핑) |
| `apps/web/quick_flow.md` | Slice 4 |
| `apps/web/mode_branching.md` | Slice 5 (yaml → TS) |
| `apps/web/direction_approval.md` | Slice 3 (verbose) / Slice 4 (minimal) |
| `apps/web/wireframes/*` | Slice 2/3/4 (구현 시 참조) |

---

## 외부 의존성

| 서비스 | 용도 | Phase 3 |
|---|---|---|
| OpenAI API | LLM 호출 | Phase 1 endpoint 활용 (mock 모드도 가능) |
| Supabase | DB | Phase 1 graceful skip (없어도 동작) |
| pgvector | RAG | Phase 1 graceful fallback |

→ Phase 3은 frontend phase. backend는 Phase 1 baseline 그대로.

---

## 도구 의존성

| 도구 | 용도 |
|---|---|
| Node.js 20+ | Next.js 14 |
| npm | 패키지 관리 |
| Python 3.11 | pytest (회귀) + audit_naming |
| PowerShell 5.1 | sanity / audit_page_component |
| Git | commit / push |

---

## 코드 의존성 (apps/web/package.json, Phase 1 설치 이미 완료)

기존:
- next@14, react@18, react-dom@18
- typescript@5
- tailwindcss
- (Phase 1) ESLint, Prettier (선택)

Phase 3에서 추가 가능 (선택):
- clsx (조건부 className)
- zod (선택, runtime 검증)

→ Phase 3은 새 패키지 install 최소화. 기존 패키지 활용 권장.

---

## Phase 3 → Phase 4 인수 항목

| ID | 항목 | 이관 사유 |
|---|---|---|
| D2 | QuickInputCard alt variants | 실 사용 후 alt 결정 (Phase 9 피드백 데이터) |
| D3 | PlanCard 4-layer 정합 | **조정 3번 — Phase 4 활성화 시 PlanComparisonCard와 함께 재정의** |
| D4 | PlanComparisonCard 상세 spec | Phase 4 3-plan 활성화 |

---

## 주의사항

- Phase 3은 spec phase가 아니라 **구현 phase** — design 결정 0건
- component_map.md / design_handoff.md 등 Phase 2 산출물은 **수정 금지** (조정 4번)
- spec ↔ 코드 drift 발견 시 deviation_log에만 기록
- sub-agent 발사 시 **P-X1 §SELF-VERIFICATION 의무 포함** (phase-start v1.3.0)
- 매 Slice 종료 시 audit_naming + pytest + next build 자동 검증
