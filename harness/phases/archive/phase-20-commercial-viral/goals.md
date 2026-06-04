# Phase 20 — Commercial Viral 모드 (output_mode 4th tier)

## 목표

`output_mode` 를 **4-tier** 로 확장: `compact < rich < director < commercial_viral`. 최상위 `commercial_viral` = **상업·전략급 기획 브리프** 모드 — 시장 맥락·시청자 심리·브랜드 포지셔닝·후크 시스템·리텐션 설계·전환 설계까지.

director(Phase 15)와 **동일 슬라이스 패턴**(schema→prompt→wiring→critic→frontend→verify), 전부 **gated / additive / OFF byte-identical**.

## 근거
- PARKED 제안서 `meta/proposals/2026-06-03_commercial-viral-mode-design.md` (선행조건 a/b/c + 데이터레이어 의존).
- 사용자 피드백(Phase 15): director=초안 수준 → 품질 보강은 commercial_viral + PKM/RAG.
- ★ 선행조건 충족: (a) rich 실사용 ✅(P13/14) · (b) 위저드 실연결 ✅(P14) · (c) human review ✅(P12 S4) · 데이터레이어(PKM/RAG) ✅(P16/17).

## 핵심 원칙 (제안서 §0·§8 리스크 보정 계승)
- **보정1**: 조회수/viral **보장 아님** — 패턴·근거 기반 전략 브리프 + 사람 검증. 보장 표현 차단.
- **보정2**: **기획 브리프 수준만** — 영상 제작(편집/TTS/BGM/자막/업로드) 영구 제외(product_boundary).
- **보정3**: market_context/audience_psychology 등은 실데이터 없으면 **LLM 추측** → 응답에 추측 표기. v1 LLM-only.
- default=compact 불변. commercial_viral 은 명시 flag + (권장) opt-in 에서만.

## 산출 (슬라이스)
S1(schema 4-tier+COMMERCIAL_FIELDS+CommercialScene) → S2(P-006 commercial 프롬프트) → S3(wiring) → S4(critic 17차원) → S5(frontend) → S6(live verify + cost + close).
