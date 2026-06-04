# Phase 20 — Non-Goals

```
- ★ commercial_viral default ON 금지 — 어떤 경우에도 default=compact 불변. 명시 flag + (권장) opt-in.
- ★ 조회수/viral 보장 금지(보정1) — 보장 표현 프롬프트 차단. measurement_plan 은 사후 학습용(보장 지표 아님).
- ★ 영상 제작 미포함(보정2, product_boundary 영구 제외) — scene_breakdown/production_feasibility/
  platform_packaging 은 기획 브리프 수준만. 편집/TTS/BGM/자막합성/업로드 = 영구 제외.
- ★ 새 MOA agent 금지 — commercial_viral = 기존 Planner/Critic 의 mode 확장(슬롯/차원 추가)일 뿐.
- 데이터레이어 신규 구축 미포함 — market_context/audience_psychology 는 v1 LLM-only(추측 표기).
  PKM/RAG 실데이터 enrichment 는 후속(기존 Phase 17 주입은 재사용 가능하나 본 phase 신규 파이프 0).
- golden5(GS-COMM-1~5) real LLM 회귀 + human review 채점 = §5.4 "paid 활성 전 게이트" → 본 phase
  build 범위 밖(default OFF 이므로 활성 게이트는 별도). eval rubric 차원 노트(additive)만 동반 가능.
- rich/director default 전환 미결정(별도) — 본 phase 는 4번째 tier 추가만.
- 토큰/비용 정밀 단가 재조정 = 데모 실측 후(§6 골격만).
```
