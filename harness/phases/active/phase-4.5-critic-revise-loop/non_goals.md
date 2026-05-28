# Phase 4.5 — Non-Goals

> Phase 4.5에서 **명시적으로 제외**하는 작업. scope creep 시 즉시 사용자 알림.

## 명시적 제외 (NG1~NG10)

| ID | 항목 | 이관 | 사유 |
|---|---|---|---|
| **NG1** | DB 영속화 (in-memory `_plan_store` → PostgreSQL) | Phase 5 | DB/Auth는 Phase 5 단일 phase로 격리 |
| **NG2** | Supabase Auth + JWT | Phase 5 | 보안 결정은 multi-llm-validation formal 필수 |
| **NG3** | Row Level Security (RLS) 정책 | Phase 5 | DB 도입과 묶음 |
| **NG4** | SSE Progress streaming (D7) | Phase 5 | 30~60초 UX는 DB/Auth와 함께 |
| **NG5** | **PlanCard.tsx 수정** (D3/D4 4-layer 정합) | Phase 5+ | **5연속 0줄 유지** (사용자 결정 6-a 계승) |
| **NG6** | PlanComparisonCard 4-layer (D8) | Phase 5+ | D3/D4와 묶음 |
| **NG7** | prompt_registry 정식 등록 (Rewriter prompt) | Phase 6+ | 본 phase는 인라인 prompt만, prompt-version-review Skill은 Phase 6+ |
| **NG8** | revise 효과 eval (golden_set FC-001~005 자동 평가) | Phase 9+ | eval-run Skill 정식화는 Phase 9+ |
| **NG9** | multi-provider client factory baseline (Z-X2) | Phase 21+ | over-engineering 회피, Anthropic/Custom 실제 도입 결정 후 |
| **NG10** | Phase 1 endpoint `/api/v1/generate` 제거 | Phase 8+ | 사용자 결정 5-a (교차 검토 + 마이그까지 완료 후 제거 예정) |

## 단어 수준 금지

다음 단어가 본 phase 신규/수정 파일에 등장하면 scope creep 신호:

- `supabase` (NG1, NG2)
- `RLS`, `row_level_security` (NG3)
- `SSE`, `EventSource`, `stream` (NG4 — 단, "stream"이 LLM streaming 의미는 허용)
- `4-layer` (NG5, NG6 — 단, ADR 등 참조 문서는 허용)
- `prompt_registry` (NG7 — Rewriter는 인라인 prompt)
- `Anthropic`, `Claude API`, `claude-3` (NG9 — multi-provider는 현 OpenAI 고정)

## 사용자 결정 6-a 계승 (PlanCard 무수정 정책)

Phase 4에서 사용자가 명시: "PlanCard 무수정 (D3/D4 모두 Phase 5+)".
Phase 4.5에서도 **동일 정신 유지**. Z-X3 best-plan highlight는 **wrapper UI** (`/plan/[plan_id]/page.tsx`)에서 처리:

```tsx
{candidates.map((plan, idx) => (
  <div
    key={idx}
    className={
      recommendedIdx === idx
        ? "ring-2 ring-emerald-500 rounded-lg"
        : ""
    }
  >
    <PlanCard plan={plan} />  {/* ← 무수정 */}
  </div>
))}
```

## 회피 패턴

- ❌ "조금만"이라며 PlanCard에 `recommended?: boolean` prop 추가
- ❌ "어차피 수정할 거" 이유로 D3/D4 함께 진행
- ❌ Rewriter prompt를 prompt_registry/에 미리 등록
- ❌ revise loop 효과를 골든셋으로 평가 (eval-run Skill 호출)
- ❌ Critic best-plan 결과를 사용자 피드백과 비교하는 metric 수집 (Phase 9+)
