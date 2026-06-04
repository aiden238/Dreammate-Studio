# Page Map

> 위치: `apps/web/page_map.md`
> 상태: Phase 2 Slice 5 통합 갱신 (2026-05-27)
> 정합 기준: `apps/web/design.md` §5, §7, §8, §9, §11, §12, §13 + Phase 2 spec
> 참조: `apps/web/discovery_flow.md`, `quick_flow.md`, `mode_branching.md`, `direction_approval.md`, `component_map.md`, `design_handoff.md`
>
> 본 파일 = 전체 routes 통합. Phase 1 active routes 보존 + Phase 2 spec routes 추가 + Phase 4+ placeholder.
> 각 route → 사용 컴포넌트 명시 (component_map.md cross-reference).

---

## 1. Active Routes (Phase 1 구현 완료, 운영 중)

### 1.1 `/` (Home / Initial Input)

- **진입 조건**: Phase 1 첫 진입 (Mode 분기 미적용 — Phase 3 진입 시 mode_branching.md 라우터로 전환)
- **표시 컴포넌트** (component_map.md):
  - textarea (자유 입력) — Phase 1 native input (별도 컴포넌트 X)
  - `SubmitButton` — Phase 1 기존 (`apps/web/components/SubmitButton.tsx`)
  - `ProgressStepper` — Phase 1 기존 (4단계 sync stepper)
- **API**: `POST /api/v1/generate` (Phase 1 simplified endpoint)
- **다음**: `/plan` (성공 시) / 같은 페이지 (에러 시 ErrorCard inline 표시)
- **Phase 3 migration**: Mode 자동 분기 진입 화면 (`mode_branching.md`)으로 전환 — `/`는 Landing 또는 Dashboard로 격상 가능

### 1.2 `/plan`

- **진입 조건**: `/`에서 generate 성공 후
- **표시 컴포넌트** (component_map.md):
  - `PlanCard` (Phase 1) — 단일 plan 표시 (Phase 1 단일 plan, Phase 4 3-plan 비교 전환)
  - `ProgressStepper` (Phase 1) — 완료 상태 표시
  - `ErrorCard` (Phase 1) — 응답 실패 시 (sessionStorage envelope 검증 실패 포함)
- **데이터 소스**: `sessionStorage.envelope` (Phase 1 임시 저장)
- **다음**:
  - "다시 만들기" → `/` 복귀
  - (Phase 4+) Plan 선택 → save → workspace
- **Phase 4 migration**: `PlanComparisonCard` 활성화 → 3-plan 가로 비교 + 1 선택 화면으로 전환 (component_map.md PlanComparisonCard placeholder 참조)

### 1.3 `/new/branding` (브랜딩 세션 — Akinator 주제발굴, Phase 18)

- **진입 조건**: `/new`에서 "주제 추천받기" 카드 클릭 (주제 미정 사용자)
- **동작**: LLM 동적 스무고개(질문 카드 + 자유입력 + 진행바) → 후보 주제 3개(톤/타깃/포맷) → 택1 → generate 연결
- **API**: `POST /plans/{id}/branding/{next,finalize,select}` (api_contract §8.6, CC-023)
- **다음**: 택1 후 `/plan/[id]` (생성 결과)

### 1.4 `/brain` (마이페이지 2nd brain — PKM 도식화·큐레이션, Phase 19)

- **진입 조건**: 홈("🧠 내 brain" 링크) / 인증 사용자. AuthGuard.
- **표시**: 모바일=scope 카드/리스트(개인/브랜드 PKM 칩 + 🔒) / 데스크톱=react-flow 그래프(lazy-load, ssr:false, ≥1024px) + 카드↔그래프 토글. 무데이터 → empty state(→ `/new/branding` 유도).
- **컴포넌트**: `components/brain/PkmGraph.tsx`(데스크톱 그래프) + `/brain/page.tsx`(카드/리스트 + 큐레이션) + `lib/use_media_query.ts`
- **API**: `GET /api/v1/me/pkm-graph` + `PATCH/DELETE /api/v1/me/pkm/{node_id}` (api_contract §8.7, CC-024)
- **큐레이션**: 잠금(locked) 토글 / 편집(content) / 삭제 — 본인 데이터(RLS + 소유 검증)

---

## 2. Spec Routes (Phase 2 spec, Phase 3 구현 예정)

> 본 section의 routes는 Phase 2에서 spec만 작성 (Next.js 코드 0줄).
> Phase 3 진입 시 Next.js app router 또는 middleware로 구현.

### 2.1 Mode 분기 진입점

#### `/new` (Mode auto-router, UI 없음)
- **진입 조건**: 사용자가 "+ 새 프로젝트" / "새 영상" 클릭 (Dashboard 또는 직접 URL)
- **동작**: `mode_branching.md` yaml 따라 자동 redirect
  - `rule_new_user` (Brand 0) → `/new/discovery/step/1`
  - `rule_brand_no_series` → `/new/discovery/step/3` (discovery_from_step3)
  - `rule_has_series` → `/new/quick`
  - `rule_default` (fallback) → `/new/discovery/step/1`
- **UI 없음**: middleware 라우팅만 (Phase 3 구현)
- **참조**: `mode_branching.md` §2 branching_rules + §4 매핑표

### 2.2 Discovery Routes (`/new/discovery/step/{1..7}`)

#### `/new/discovery/step/1` (Step 1 Brand)
- **표시 컴포넌트** (component_map.md):
  - `WizardStepHeader` (Phase 0 entry, Phase 3 신규 또는 ProgressStepper 활용)
  - `CardGrid5` (4-layer, Slice 2) — radiogroup 5장 컨테이너
  - `BrandDirectionCard` × 5 (4-layer, Slice 2) — 4 AI suggestions + 1 user_direct_input
  - `SubmitButton` (Phase 1 기존, sticky bottom)
  - `ErrorCard` (Phase 1 기존) — 응답 실패 시
- **API**: P-001 `brand_direction_cards` (output_schema.md §3)
- **다음**: `/new/discovery/step/2`
- **참조**: `discovery_flow.md` §1 Step 1 Brand 상세 + `wireframes/step1_brand.md`

#### `/new/discovery/step/2` (Step 2 Domain)
- **표시 컴포넌트**: Step 1과 동일 (CardGrid5 + BrandDirectionCard × 5 변형 + SubmitButton)
- **API**: P-002 `domain_direction_cards` (output_schema.md §4)
- **다음**: `/new/discovery/step/3`
- **참조**: `discovery_flow.md` §2

#### `/new/discovery/step/3` (Step 3 Series)
- **표시 컴포넌트**: 동상 (CardGrid5 + BrandDirectionCard × 5 변형)
- **API**: P-003 `series_cards` (output_schema.md §5)
- **다음**: `/new/discovery/step/4`
- **참조**: `discovery_flow.md` §3
- **Note**: `rule_brand_no_series` 진입점 — Brand 있고 Series 없는 사용자가 직접 이 route로 라우팅 (mode_branching.md)

#### `/new/discovery/step/4` (Step 4 Target)
- **표시 컴포넌트**: 동상
- **API**: P-004 part 1 `target_cards` (output_schema.md §6)
- **다음**: `/new/discovery/step/5`
- **참조**: `discovery_flow.md` §4

#### `/new/discovery/step/5` (Step 5 Tone, ★ 5-card 예외 form 변형)
- **표시 컴포넌트** (5-card 예외):
  - `WizardStepHeader`
  - `ToneChipsForm` (Phase 3 신규 — Phase 2는 sketch만, Phase 3 진입 시 4-layer 작성) — 다중선택 chip + 직접 입력 textarea
  - `SubmitButton` (sticky)
- **API**: P-004 part 2 `tone_card` form (output_schema.md §7)
- **다음**: `/new/discovery/step/6`
- **참조**: `discovery_flow.md` §5 (U2-7 confirmed: 다중선택 chip 패턴)

#### `/new/discovery/step/6` (Step 6 Direction Summary)
- **표시 컴포넌트**:
  - `WizardStepHeader`
  - `DirectionApprovalCard` (4-layer, Slice 3) — **variant=verbose** (Discovery 권장 chosen)
- **API**: P-005 `oneline_direction` (output_schema.md §7)
- **다음**:
  - "이대로 진행" → `/new/discovery/step/7`
  - "수정 후 진행" → `/new/discovery/step/7` (편집된 텍스트 전달)
  - "다시 생성" → 본 route 재호출 (revise_count++)
- **참조**: `direction_approval.md` + `discovery_flow.md` §6 + `wireframes/direction_approval.md`

#### `/new/discovery/step/7` (Step 7 Generate)
- **표시 컴포넌트**:
  - `WizardStepHeader`
  - `ProgressStepper` (Phase 1 기존, 4단계: Intent → RAG → Planning → Critic)
  - `RAGReferencePanel` (Phase 0 entry, Phase 4+ SSE 활성 시)
  - `PlanCard` (Phase 1 기존) — 생성 완료 시 (Phase 1은 단일 plan)
  - `ErrorCard` (Phase 1 기존) — 응답 실패 시
- **API**: P-006 `plan_candidates` (output_schema.md §8) — Phase 1은 1 plan, Phase 4는 3 plans
- **다음**: `/plan` (생성 완료 시) — Phase 4에서는 `/brand/[brandId]/.../video/[videoId]` workspace로 전환
- **대기 시간**: 30~60초 (`design.md` §13)
- **참조**: `discovery_flow.md` §7

### 2.3 Quick Mode Routes (`/new/quick*`)

#### `/new/quick` (Step 1 짧은 프롬프트)
- **표시 컴포넌트**:
  - `BreadcrumbBrandPath` (Phase 0 entry) — 상속된 Brand/Domain/Series 표시
  - `QuickInputCard` (4-layer, Slice 4, **mode='initial_prompt'**)
  - `SubmitButton` (Phase 1 기존, sticky)
  - `IntentWarningBox` (Phase 0 entry) — 영상기획 외 입력 감지 시
- **API**: `POST /api/v1/quick/start` (Phase 4 endpoint)
  - body: `{ short_prompt, brand_id, series_id, locale }`
  - response: `{ needs_clarification: true, clarify_questions: [...] }` 또는 P-005 즉시
- **다음**:
  - `needs_clarification: true` → `/new/quick/clarify`
  - `needs_clarification: false` → `/new/quick/direction`
- **참조**: `quick_flow.md` §1

#### `/new/quick/clarify` (Step 2 부족 정보 질문, optional)
- **표시 컴포넌트**:
  - `BreadcrumbBrandPath`
  - `QuickInputCard` (재사용, **mode='follow_up_question'**) — question + textarea + skip CTA
  - `SubmitButton` (primary + skip 2-way)
  - (대안 패턴) `IntentQuestionCard` (Phase 0 entry) — 4지선다 + 자유 입력 — Phase 3 결정 시 활성
- **API**: 진입 시점은 Step 1 응답의 `clarify_questions`. 답변 submit 시 `POST /api/v1/quick/answer` (Phase 4) → P-005 응답
- **다음**: `/new/quick/direction`
- **참조**: `quick_flow.md` §2

#### `/new/quick/direction` (Step 3 Direction Approval)
- **표시 컴포넌트**:
  - `BreadcrumbBrandPath`
  - `DirectionApprovalCard` (4-layer, Slice 3, **variant=minimal** — Quick 권장)
- **API**: P-005 `oneline_direction` (output_schema.md §7)
- **다음**:
  - "이대로 진행" → `/new/quick/generate`
  - "수정 후 진행" → `/new/quick/generate` (편집된 텍스트)
  - "다시 좁히기" → `/new/discovery/step/1` (mode_branching.md override `direction_renarrow`)
- **참조**: `quick_flow.md` §3 + `direction_approval.md` §2.2

#### `/new/quick/generate` (Step 4 Generate)
- **표시 컴포넌트**:
  - `BreadcrumbBrandPath`
  - `ProgressStepper` (Phase 1 기존, 4단계)
  - `PlanCard` (Phase 1 기존) — 생성 완료 시
  - `ErrorCard` (Phase 1 기존)
- **API**: P-006 `plan_candidates` (output_schema.md §8) — Discovery Step 7과 동일 endpoint
- **다음**: `/plan` (생성 완료 시)
- **대기 시간**: 30~60초
- **참조**: `quick_flow.md` §4

---

## 3. Route ↔ Mode Branching 매핑

| 사용자 상태 | 자동 분기 | 진입 라우트 | rule_id (mode_branching.md) |
|---|---|---|---|
| 신규 (Brand 0) | Discovery | `/new/discovery/step/1` | rule_new_user |
| Brand 있음, Series 0 | Discovery from Step 3 | `/new/discovery/step/3` | rule_brand_no_series |
| Series 있음 | Quick | `/new/quick` | rule_has_series |
| 명시 "새로 시작" | Discovery (강제) | `/new/discovery/step/1` | user_new_project (override) |
| 명시 "Quick" (Brand 있음) | Quick (강제) | `/new/quick` | user_quick_force (override) |
| Quick Mode "다시 좁히기" | Discovery (전환) | `/new/discovery/step/1` | direction_renarrow (override) |
| 분류 불가 | Discovery (fallback) | `/new/discovery/step/1` | rule_default |

→ 전체 라우팅 정책은 `mode_branching.md` §4 매핑표 참조.

---

## 4. Future Phase Routes (placeholder)

### 4.1 Phase 4 (MOA Lite 완성)
- `/plan` — `PlanComparisonCard` (4-layer 신규) 활성 → 3-plan 가로 비교 + 1 선택
- `/brand/[brandId]/.../video/[videoId]` — Project Workspace (design.md §8.9) 일부 활성
- `/brand/.../video/[videoId]/output` — Final Output (design.md §8.10) 일부 활성

### 4.2 Phase 5 (Auth)
- `/login` — Supabase Auth
- `/signup` — Supabase Auth (신규 가입 흐름)
- `/onboarding` — 신규 회원 첫 Brand 생성 (design.md §8.3)
- `/dashboard` — 기존 사용자 진입점 (design.md §8.4)

### 4.3 Phase 9 (Feedback / History)
- `/history` — 저장된 기획안 목록 (`design.md` §8 보조 `/saved` 자리)
- `/feedback` — 사용자 피드백 화면 + choice_logs UI

### 4.4 Phase 11+ (확장)
- `/settings` — Brand Memory 관리, 계정, dark mode, 다국어 (design.md §8 보조)
- `/brand-memory/[brandId]` — Brand 단위 메모리 편집
- `/knowledge` — LLM Wiki + Custom RAG 관리

### 4.5 영구 제외 (MVP non-goals)
- `/billing` — 결제 (영구 제외, mvp_non_goals.md)
- `/team` — 팀 workspace (영구 제외)
- `/admin` — 관리자 대시보드 (영구 제외)

---

## 5. Phase 1 → Phase 2 → Phase 3 라우팅 진화

```
Phase 1 (현재 운영)
  /        — 자유 입력 (textarea)
  /plan    — 단일 PlanCard

Phase 2 spec (본 파일)
  /        — Phase 1 유지 (Phase 3에서 mode router로 전환)
  /plan    — Phase 1 유지 (Phase 4에서 PlanComparisonCard 활성)
  /new     — Mode auto-router (Phase 3 구현)
  /new/discovery/step/{1..7}  — Discovery 7-step (Phase 3 구현)
  /new/quick                  — Quick Step 1 (Phase 3 구현)
  /new/quick/clarify          — Quick Step 2 (Phase 3 구현)
  /new/quick/direction        — Quick Step 3 (Phase 3 구현)
  /new/quick/generate         — Quick Step 4 (Phase 3 구현)

Phase 3 (Next.js PWA)
  → 본 spec의 모든 routes를 실 코드로 구현
  → /는 Mode router 또는 Landing으로 격상 검토

Phase 4 (MOA Lite + 3-plan)
  → /plan에 PlanComparisonCard 활성
  → /brand/[brandId]/... workspace 추가
```

---

## 6. 변경성 (replaceability_score.md §3.3 정합)

| 변경 | 영향 파일 | 비용 |
|---|---|---|
| 신규 route 추가 (예: `/new/voice`) | `page_map.md` + `component_map.md` + 새 flow.md | M |
| route 폐기 (예: `/new/quick*` 제거) | `page_map.md` + `mode_branching.md` + `quick_flow.md` + `component_map.md` | H |
| Discovery step 수 변경 (7 → 5) | `page_map.md` + `discovery_flow.md` + `mode_branching.md` + (wireframes) | H |
| Phase 1 route 유지 정책 변경 (예: `/`를 Dashboard로) | `page_map.md` (1줄) + Phase 5+ 구현 | L (spec) / M (구현) |
| 새 컴포넌트가 기존 route에 추가 (예: /plan에 RegenerateButton) | `page_map.md` (1줄) + `component_map.md` | L |

→ 상세 변경 절차는 `design_handoff.md` §1 + §2 참조.

---

## 7. cross-reference 정합 (manual checklist)

본 page_map.md의 모든 컴포넌트가 component_map.md에 등재되어 있어야 함.

- [ ] `SubmitButton` — component_map.md Feedback / Action (Phase 1)
- [ ] `ProgressStepper` — component_map.md AI Flow 또는 Phase 1 entry
- [ ] `PlanCard` — component_map.md Output (Phase 1 simplified) 또는 PlanOptionCard (Phase 0 entry)
- [ ] `ErrorCard` — component_map.md (Phase 1 추가 entry)
- [ ] `WizardStepHeader` — component_map.md Discovery
- [ ] `CardGrid5` — component_map.md Phase 2 Slice 2 (4-layer)
- [ ] `BrandDirectionCard` — component_map.md Phase 2 Slice 2 (4-layer)
- [ ] `DirectionApprovalCard` — component_map.md Phase 2 Slice 3 (4-layer)
- [ ] `QuickInputCard` — component_map.md Phase 2 Slice 4 (4-layer)
- [ ] `ToneChipsForm` — component_map.md (Phase 3 deferred entry, Slice 5 표기)
- [ ] `BreadcrumbBrandPath` — component_map.md Layout / Navigation
- [ ] `IntentWarningBox` — component_map.md Project Memory / Intent
- [ ] `IntentQuestionCard` — component_map.md Input Components
- [ ] `RAGReferencePanel` — component_map.md AI Flow
- [ ] `PlanComparisonCard` — component_map.md Phase 4 placeholder (Slice 5)

→ Slice 6 design-review Skill 호출 시 본 체크리스트 자동 검증.

---

## 8. 변경 이력

- Phase 0: design.md §8 MVP Pages 10개 baseline (`/`, `/login`, `/onboarding`, `/dashboard`, `/new/discovery`, `/new/direction`, `/new/quick`, `/new/generate`, `/brand/[brandId]/.../video/[videoId]`, `/brand/.../output`)
- Phase 1: `/`, `/plan` 2 routes 활성 (simplified MVP)
- 2026-05-27: Phase 2 Slice 5 — 통합 갱신
  - Phase 1 active routes 보존
  - Phase 2 spec routes 추가 (`/new`, `/new/discovery/step/{1..7}`, `/new/quick*`)
  - 각 route → 사용 컴포넌트 명시
  - Route ↔ Mode Branching 매핑 표 추가
- 2026-06-04: Phase 18/19 active routes 추가
  - §1.3 `/new/branding` (Akinator 주제발굴, CC-023)
  - §1.4 `/brain` (2nd brain PKM 도식화·큐레이션, CC-024) — 모바일 카드 / 데스크톱 react-flow 하이브리드
  - Future Phase routes placeholder 정리
  - cross-reference 정합 checklist 추가
