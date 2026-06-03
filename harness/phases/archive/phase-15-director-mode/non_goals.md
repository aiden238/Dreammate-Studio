# Phase 15 — Non-Goals (명시적 제외)

| ID | 제외 항목 | 사유 / 이연처 |
|---|---|---|
| NG1 | **commercial_viral tier** (market_context/audience_psychology/brand_positioning/commercial_conversion/platform_packaging/production_feasibility/measurement_plan + scene 상업필드 brand_signal/commercial_signal) | 시장/트렌드 품질이 **PKM/RAG 데이터레이어에 종속**(제안서 보정3 + §7.2). 데이터레이어(로드맵 ③) 선행. director 는 데이터 비의존 슬롯만. |
| NG2 | **PKM/RAG 데이터레이어** (개인/brand PKM, 공용 Wiki, Trend Snapshot, retrieval orchestrator) | 로드맵 ③ — 별도 기획안(`2026-06-03_pkm-rag-orchestrator-design.md`). |
| NG3 | **rich/director default ON 전환** | gated OFF 유지. default 승격은 cost+human review 합의 후 별도 결정. |
| NG4 | **완성 대본 / 영상 제작·편집·TTS·BGM·업로드** | product_boundary 영구. scene_breakdown 은 "기획 의도/감정/리텐션 근거"이지 촬영 지시·완성 대본 아님(제안서 보정2). |
| NG5 | **17차원 Critic / commercial 8차원** | commercial_viral 영역(NG1). director 는 기존 9차원 + retention_design 1개만(gated). |
| NG6 | **검증 보강(human review 실채점 + 전수 eval)** | 로드맵 ② — director 다음 단계(별도). 본 phase 는 director 빌드 + 자동 게이트(byte-identical + depth 측정)까지. |
| NG7 | **조회수/viral 보장 표현** | 제안서 보정1 — director 프롬프트도 보장 표현 금지(기존 광고 과장 차단 계승). |

★ NG1 이 핵심 — director 는 **데이터레이어 비의존 중간 tier**로 한정(연출·리텐션). 시장/브랜드/전환 = commercial_viral(PKM/RAG 후). 이게 제안서 §7.1 단계화(director 먼저, 데이터 비의존) + 사용자 로드맵과 정합.
