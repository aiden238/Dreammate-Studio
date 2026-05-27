# Quick Mode Flow

> 위치: `apps/web/quick_flow.md`
> 상태: Phase 2 Slice 4 baseline (2026-05-27)
> 참조: `apps/web/design.md` §12, `apps/web/mode_branching.md`, `apps/web/direction_approval.md` (Slice 3), `apps/web/component_map.md` (QuickInputCard / DirectionApprovalCard), `docs/contracts/output_schema.md` §7~§8
>
> 원칙: 기존 Brand / Domain / Series 컨텍스트가 있는 사용자를 위한 단축 흐름.
> Mode 자동 분기 시 `user.current_brand.series.count >= 1` → Quick Mode (`mode_branching.md` §2 rule_has_series).

---

## 0. 개요

### 0.1 흐름 도식

```
짧은 프롬프트 입력 → 부족 정보 1~2 질문 → DirectionApprovalCard (minimal) → Generate (P-006)
   (QuickInputCard)      (QuickInputCard 재사용)        (Slice 3)              (Phase 1 컴포넌트 재사용)
                              ↓ (사용자 답변)
                       완성된 컨텍스트
```

### 0.2 Discovery와의 차이

| 항목 | Discovery | Quick |
|---|---|---|
| 단계 수 | 7-step wizard | 2~4-step short |
| 카드 5장 패턴 | Step 1~4 모두 사용 | 사용 안 함 (단일 input) |
| 부족 정보 질문 | 단계별 누적 | 1~2개만 동적 노출 |
| Direction Approval variant | minimal 또는 verbose | **minimal 권장** |
| 진입 조건 | Brand 컨텍스트 없음 / 명시 'new project' | Series 컨텍스트 있음 |
| 예상 소요 시간 | 3~5분 | 30초~1분 |

### 0.3 공통 정책

- 모든 step은 BreadcrumbBrandPath 상단 표시 (현재 컨텍스트: Brand · Domain · Series)
- back navigation: 이전 step state 보존 (sessionStorage)
- mobile 360px first (`apps/web/design.md` §17, `tokens.md` §5.1 `bp.mobile`)
- a11y: focus management + `aria-live="polite"` for dynamic question 노출 (`docs/contracts/frontend_design_contract.md` §5)
- 세션 저장: Phase 2 spec 단계 — sessionStorage (Phase 5 Auth + DB 저장 도입 시 교체)
- 200자 초과 시 `QuickPromptInput` 줄임 제안 (component_map.md Input Components 기존 entry, `onShorten`)

### 0.4 라우팅 (Phase 3 진입 시 활성)

```
/new                       → Mode 자동 분기 router (mode_branching.md)
/new/quick                 → Step 1 짧은 프롬프트 입력
/new/quick/clarify         → Step 2 부족 정보 질문 (optional, AI 판단 시만)
/new/quick/direction       → Step 3 Direction Approval (DirectionApprovalCard minimal)
/new/quick/generate        → Step 4 Generation Progress
```

→ Phase 2는 spec only. 실 routing 구현은 Phase 3.

---

## 1. Step 1: 짧은 프롬프트 입력

### 1.1 목적

- 기존 Brand/Series 컨텍스트가 있는 사용자가 "이번엔 이렇게" 의도만 짧게 표현
- 결과: AI가 컨텍스트 검사 후 부족 정보 식별 → Step 2 (부족 시) 또는 Step 3 (충분 시)

### 1.2 사용 컴포넌트

- `QuickInputCard` (mode='initial_prompt') — `component_map.md` 참조 (Slice 4)
- `BreadcrumbBrandPath` (Phase 0 기존) — 상단 컨텍스트 표시
- `SubmitButton` (Phase 1 기존, sticky bottom) — value 비어있으면 비활성
- `IntentWarningBox` (Phase 0 기존) — 영상기획 외 입력 감지 시

### 1.3 API 호출

- **submit 시**:
  - request: `POST /api/v1/quick/start` (Phase 4 endpoint)
  - body: `{ short_prompt: string, brand_id: uuid, series_id: uuid, locale: "ko-KR" }`
  - response: 부족 정보 판정 결과
    - `needs_clarification: true` → `clarify_questions: [{ id, text, suggested_options? }]` (1~2개)
    - `needs_clarification: false` → P-005 `oneline_direction` (output_schema.md §7) 바로 반환
- Phase 2 spec 단계: sessionStorage에 short_prompt 저장 후 fixture 응답으로 다음 step 라우팅

### 1.4 State / Events

```
state:
  - shortPrompt: string ('' ~ 300자)
  - loading: boolean
  - error: ErrorEnvelope | null

events:
  - onChange(text: string)          → QuickInputCard textarea
  - onSubmit()                       → API 호출 + 결과별 라우팅
```

### 1.5 응답/에러 상태 (`design.md` §20 정합)

- **empty**: textarea 빈 상태 + submit 비활성
- **loading**: submit 후 spinner (`tokens.motion.fast`)
- **error**: ErrorCard (Phase 1 기존) — INV-001 입력 검증 / E-LLM-* LLM 실패
- **intent_off_topic**: IntentWarningBox 부드러운 안내 (영상기획 외 입력 감지 시)

### 1.6 a11y

- 페이지 aria-label: "Quick Mode 짧은 프롬프트 입력"
- textarea: `role="textbox" aria-multiline="true"` + `aria-label="이번 영상 의도"`
- char count: `aria-live="polite"` (300자 근접 시 알림)
- 키보드: Tab 진입 → 입력 → Cmd/Ctrl+Enter로 submit

### 1.7 Wireframe

`apps/web/wireframes/quick_short.md` Step 1 참조 (ASCII art, 360px 적합).

---

## 2. Step 2: 부족 정보 1~2 질문 (Optional)

### 2.1 목적

- AI(P-002~P-004 partial)가 short_prompt + 기존 컨텍스트 검사 후 부족 정보 식별
- 1~2개만 질문 (Discovery 7-step과 핵심 차별점)
- 결과: 답변 → Step 3 Direction Approval

### 2.2 사용 컴포넌트

- `QuickInputCard` (mode='follow_up_question') — 재사용
- `IntentQuestionCard` (Phase 0 기존 entry) — 4지선다 + 자유 입력 (대안 패턴)
- `SubmitButton` (Phase 1 기존) — "이대로 진행" (skip) / "답변 후 진행" 2-way

### 2.3 부족 정보 판정 로직 (backend, Phase 3+ 영역)

```
검사 항목 (P-002~P-004 partial):
  - target 없음 → "어떤 분께 보여드릴 영상인가요?"
  - tone 모호 → "느낌은? (예: 친근 / 정보형 / 유머)"
  - format 미정 → "영상 길이는? (쇼츠 30초 / 릴스 60초 / 유튜브 3~8분)"
  - message 모호 → "영상에서 가장 전하고 싶은 메시지는?"

최대 노출: 2개 (output_schema.md §7.2 missing_info Quick Mode 0~2개 규칙 정합)
```

### 2.4 State / Events

```
state:
  - clarifyQuestions: { id, text, suggested_options?[] }[]
  - answers: Record<question_id, string>
  - loading: boolean
  - error: ErrorEnvelope | null

events:
  - onAnswerChange(question_id, text)  → QuickInputCard textarea
  - onSubmitAll()                       → 모든 답변 + short_prompt POST
  - onSkip()                             → 답변 없이 Step 3 진행 (output_schema §7.2 missing_info에 자동 기록)
```

### 2.5 응답/에러 상태

- **empty**: 질문은 항상 존재 (1~2개), 답변 textarea 빈 상태
- **loading**: submit 후 spinner
- **error**: ErrorCard

### 2.6 Wireframe

`apps/web/wireframes/quick_short.md` Step 2 참조.

---

## 3. Step 3: Direction Approval (양 모드 공통)

### 3.1 사용 컴포넌트

- `DirectionApprovalCard` (variant=**minimal**) — `apps/web/direction_approval.md` 참조 (Slice 3 작성)

### 3.2 진입 조건 + variant 선택 사유

- Quick Mode는 짧은 흐름 권장 → minimal variant (한 줄 + 3-way 버튼)
- variant 자체는 `component_map.md` DirectionApprovalCard variants yaml (Slice 3 등재)에서 `chosen` toggle로 swap

### 3.3 API + 다음

- prompt: P-005 oneline_direction (output_schema.md §7)
- 사용자 액션:
  - "승인" → Step 4 Generate
  - "수정" → DirectionApprovalCard 인라인 편집 모드 (one_line textarea)
  - "다시 좁히기" → Discovery 진입 (mode_branching.md `user_new_project` override)

### 3.4 cross-reference 정합

- discovery_flow.md §6도 DirectionApprovalCard 사용 (variant 동일 또는 verbose 둘 다 가능)
- quick_flow.md (본 문서) §3에서도 DirectionApprovalCard 사용 — **컴포넌트 1개를 양 모드 공유**

---

## 4. Step 4: Generate

### 4.1 사용 컴포넌트

- `GenerationProgressStepper` (Phase 0 기존 entry) — 4단계 (Intent / RAG / Plan / Critic)
- `PlanOptionCard` × 3 (Phase 0 기존 entry) — Phase 4 활성 시 결과 페이지

### 4.2 prompt + 결과

- prompt: P-006 plan_candidates (output_schema.md §8)
- Discovery Step 7과 동일 컴포넌트 / 동일 endpoint
- 다음: `/plan` 결과 페이지 (Phase 4)
- 대기 시간: 30~60초 (`design.md` §13)

---

## 5. Mode Branching 진입 조건

- 어떤 조건에서 Quick Mode 진입하는지: `mode_branching.md` §2 참조
- 핵심 규칙: `user.current_brand.series.count >= 1` → Quick (rule_has_series, priority 3)
- 사용자 명시 "새로 시작" 선택 시 Discovery 강제 (override `user_new_project`)
- 사용자 명시 "quick mode" 강제 시 Quick (override `user_quick_force`, Brand 있을 때만)

---

## 6. Phase 별 진화

| Phase | 변경 |
|---|---|
| Phase 2 (현재) | spec only — quick_flow.md + mode_branching.md + wireframes/quick_short.md + QuickInputCard 4-layer |
| Phase 3 | Next.js 구현 — `/new/quick` 라우트 추가, QuickInputCard.tsx 작성 |
| Phase 4 | MOA Lite + multi-step endpoint 활용, SSE progress, P-005q 활성 |
| Phase 9 | 실 사용자 데이터로 Quick 진입율 분석 + 분기 임계값 조정 (mode_branching.md §2 priority 재조정) |
| Phase 11+ | dark mode + 다국어 지원 시 Quick Mode 텍스트 자원화 |

---

## 7. 변경성 (replaceability_score.md §3.3 정합)

| 변경 | 영향 파일 | 비용 |
|---|---|---|
| Quick Mode 부족정보 질문 수 변경 (2→3) | `quick_flow.md` 1줄 + backend logic (Phase 3+) | L |
| Quick Mode 단계 추가 (Step 5 신규) | `quick_flow.md` + `mode_branching.md` + `wireframes/quick_short.md` + `page_map.md` | M |
| Quick Mode 폐기 | `quick_flow.md` 삭제 + `mode_branching.md` 전면 재작성 + `page_map.md` + `component_map.md` (QuickInputCard 제거) | H |
| Direction Approval variant Quick 모드에서 verbose로 변경 | `component_map.md` DirectionApprovalCard variants chosen 토글 (Slice 3 영역) + `quick_flow.md` §3.2 1줄 | L~M |
| QuickInputCard variants 추가 (예: 음성 입력 variant) | `component_map.md` QuickInputCard variants yaml | L |

---

## 8. Open Questions (Phase 3 진입 전 확정 권장)

1. Step 2 부족 정보 질문 — `QuickInputCard` 단일 textarea vs `IntentQuestionCard` 4지선다 (Phase 3 사용자 테스트 후 결정)
2. 200자 초과 줄임 제안 활성 여부 — `QuickPromptInput.onShorten` (component_map.md Input Components 기존) 통합 vs 별도
3. Step 1 직후 LLM intent 분석 시간 — empty / loading transition UX (Phase 4 SSE 도입 시 부분 결과 노출)
4. "이대로 진행" skip 활성 정책 — 항상 vs 질문 수 ≤ 1일 때만

---

## 9. 변경 이력

- 2026-05-27: Phase 2 Slice 4 — quick_flow.md 최초 작성 (Step 1~4 + Mode Branching 연동 + QuickInputCard 4-layer cross-reference)
