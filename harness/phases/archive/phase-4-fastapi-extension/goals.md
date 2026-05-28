# Phase 4 — Goals

> Phase: 4 / FastAPI 기본 백엔드 구현 (확장)
> Status: active
> Started: 2026-05-28
> GPT 검토 채택: 6 Slices → 4 Slices (revise loop / SSE / PlanComparisonCard 4-layer는 Phase 5+ 이관)

---

## 핵심 목표

**"기존 /generate 유지 + 새 /plans/{plan_id}/generate 추가 + 3-plan 응답 + Critic verdict 구조 + 기존 프론트 회귀 없음"** — 그 이상도 그 이하도 아님.

### 본질 정의

| 종전 (원안 6 Slices) | **Phase 4 (재조율 4 Slices)** |
|---|---|
| 3-plan + Critic revise + SSE + 4-layer 재정의 | **3-plan + Critic verdict 노출만** |
| 18~26h | **7~11h** |
| 위험 8개 | **위험 6개** |

### 세부 목표

#### G1. Contract Endpoint Migration (Slice 1)
- `POST /api/v1/plans/start` — 신규 plan_id 발급
- `POST /api/v1/plans/{plan_id}/wizard/{step}` — Discovery 7-step API (skeleton)
- `POST /api/v1/plans/{plan_id}/generate` — skeleton
- `GET /api/v1/plans/{plan_id}` — 최종 결과 조회
- Phase 1 `/api/v1/generate` `X-API-Deprecation` header만 추가 (실 동작 무변경)

#### G2. 3-plan Generation (Slice 2) — Multi-model 가능 구조 ★
- **3 parallel async call** (`asyncio.gather`) — 사용자 결정 4-b
- 각 plan마다 **model 파라미터 분리 가능** (향후 multi-provider 확장)
- approach_label 3개 unique (narrative / informational / 외 1)
- `body.plan_candidates` length 3 활성
- `validation.warnings`에서 `phase_1_single_plan` 제거

#### G3. Frontend 3-plan minimal (Slice 3)
- `/plan/[plan_id]/page.tsx` 신규 (PlanCard × 3 단순 list)
- **PlanCard.tsx 무변경** (사용자 결정 6-a, D3/D4는 Phase 5+)
- Phase 1 `/plan` 페이지 회귀 0
- Phase 3 `/new/*` routes 회귀 0

#### G4. Final + Archive (Slice 4)
- audit + smoke + 변경성 회귀
- retrospective
- archive 이동
- **다음 phase 결정 (사용자 결정 3-c)** — closing_notes / retrospective에서 사용자 선택지 제시

---

## 우선순위

```
G1 (Foundation) > G2 (Thin Vertical, 3-plan) > G3 (Frontend minimal) > G4 (Final)
```

G2가 핵심 — multi-model 가능 구조 + 3 parallel call로 인프라 baseline 마련.

---

## 비-목표 (non_goals.md 참조)

- ❌ Critic revise loop + Rewriter (P-008) — **Phase 4.5 또는 다음 phase에서 결정**
- ❌ SSE Progress streaming — **Phase 5+ 이관** (Auth와 함께)
- ❌ PlanComparisonCard 본격 4-layer — **Phase 5+ 이관** (사용자 데이터 후)
- ❌ D3 PlanCard 4-layer 재정의 — **Phase 5+ 이관** (D4와 함께)
- ❌ Phase 1 endpoint 제거 — **Phase 8+ (마이그 완료 후)** (사용자 결정 5-a)
- ❌ component_map.md 갱신 — 조정 4번 절대 유지 (PlanComparisonCard placeholder는 contract-change 필요 시 별도)

---

## 사용자 결정 명세 (반영)

```yaml
decisions:
  1: a  # 4 Slices 채택
  2: a  # Sequential 4 Waves
  3: c  # 다음 phase = Slice 4 retrospective에서 결정
  4: b + multi-model  # 3 parallel call + 향후 모델 추가 가능 구조
  5: a  # Phase 1 endpoint Phase 8+ 제거 (교차 검토 + 마이그 완료 후)
  6: a  # PlanCard Phase 4 무수정 (D3/D4 모두 Phase 5+)
  7: a  # 그대로 진입
  8: deferred 명시  # 미반영 부분 다음 phase 이관
```

---

## 관련 문서

- `scope.md` — Slice별 작업 범위
- `acceptance.md` — A1~A10 완료 기준
- `assumptions.md` — phase-start v1.3.0 §6 4점검 결과
- `work_plan.md` — Slice 1~4 분해
- `multi_slice_plan.md` — Wave 1~4 (모두 순차)
- `handoff.md` — Phase 4 → 다음 phase 이관
- `docs/decisions/phase_4_endpoint_migration.md` (ADR-014, Slice 1 작성)
- `docs/decisions/phase_4_3plan_multi_model.md` (ADR-015 — multi-model 가능 구조, Slice 2 작성)
