# Phase 4 — Non-Goals

> 명시적으로 **하지 않을 것** (GPT 검토 반영, scope creep 방지).

---

## Phase 4에서 하지 않을 것

### Backend AI / MOA

- ❌ Critic revise loop (revise verdict → Rewriter 호출 → 재평가) — **Phase 4.5 또는 다음 phase**
- ❌ Rewriter Agent (P-008) 신규 작성 — Phase 4.5+
- ❌ SSE Progress streaming endpoint — **Phase 5+** (Auth와 함께)
- ❌ Long polling progress 채널 — Phase 5+
- ❌ Multi-provider 실 LLM 연결 (Anthropic 등) — **구조만 Slice 2에서 마련**, 실 연결은 Phase 21+

### Frontend

- ❌ `PlanComparisonCard` 본격 4-layer + variants — **Phase 5+** (D4, 사용자 데이터 후)
- ❌ `PlanCard` 4-layer 재정의 — **Phase 5+** (D3, D4와 함께)
- ❌ `ProgressStepper` SSE 실시간 연결 — Phase 5+
- ❌ `lib/sse_client.ts` 신규 — Phase 5+
- ❌ Discovery / Quick UI 변경 — Phase 3 산출물 그대로 활용

### Endpoint / Migration

- ❌ Phase 1 `/api/v1/generate` 제거 — **Phase 8+** (교차 검토 + 마이그 완료 후, 사용자 결정 5-a)
- ❌ Phase 1 endpoint 사용 차단 (deprecated header만 추가, 실 동작 무변경)
- ❌ frontend Phase 1 page 강제 redirect (소프트 안내만)

### Contract / Spec

- ❌ `component_map.md` 갱신 — **조정 4번 절대 유지 (11+ 연속 0줄 목표)**
- ❌ `page_map.md` 신 route 등록 — contract-change Skill 필요 시 별도 (Slice 4에서 검토)
- ❌ `design_handoff.md` 갱신 — Slice 4 변경성 회귀 walkthrough에서 실측만 기록 (Phase 2 spec 유지)
- ❌ `output_schema.md` 수정 — 이미 §8 plans length 3 명시됨, Phase 4는 코드 정합만

### Infra / DB

- ❌ DB schema 변경 — Phase 5 Auth/RLS에서
- ❌ Supabase Auth 도입 — Phase 5
- ❌ pgvector 본격 데이터 인입 — Phase 7 RAG
- ❌ CI/CD 파이프라인 — Phase 10
- ❌ 배포 (Vercel / AWS) — Phase 10

### Eval / Quality

- ❌ failure_cases FC-001~005가 revise loop으로 approve 전환 검증 — Phase 4.5+
- ❌ golden_set 11 회귀 자동화 — Phase 7+ (eval-run 본격화)
- ❌ Human review 5 샘플 — Slice 4 manual (선택)

### 영구 제외 (mvp_non_goals.md §1)

- ❌ 자동 영상 생성 / 편집
- ❌ TTS / BGM
- ❌ 자동 업로드

---

## 경계 위반 판단

요청이 위 목록에 있으면:
1. 즉시 거절 — "Phase 4 non-goals"
2. Phase 매핑 (Phase 4.5 / 5+ / 8+ / 21+ 어디로)
3. 예외는 `meta/proposals/` + `contract-change` Skill + 사용자 승인

---

## 의도된 단순화 정책 (Phase 4 → 다음 phase 인수)

다음은 "Phase 4에서 안 하는 것"이 아니라 **의도된 deferred** (closing_notes에 명시):

| 항목 | Defer 대상 | 이유 |
|---|---|---|
| D6 Critic revise loop + Rewriter | Phase 4.5 또는 다음 phase | cost / latency / 무한 루프 위험 — 별도 mini-phase로 분리 |
| D7 SSE Progress streaming | Phase 5+ | Auth/RLS와 함께 인프라 변경 |
| D8 PlanComparisonCard 본격 4-layer | Phase 5+ | 사용자 실 데이터 누적 후 의미 있는 variants 도출 |
| D3 PlanCard 4-layer 재정의 | Phase 5+ | D4와 함께 처리가 자연 |
| D2 (Phase 3 인수 유지) QuickInputCard alt variants | Phase 9 | 사용자 피드백 후 |

→ 이 항목들은 Phase 4 closing_notes + Slice 4 retrospective에 **자동 인수 명시**.

---

## 변경 절차

non_goals 변경 (Phase 4 scope 확장) 시:
1. `meta/proposals/` 제안
2. `contract-change` Skill
3. **multi-llm-validation 필수** (큰 결정)
4. 사용자 최종 승인
