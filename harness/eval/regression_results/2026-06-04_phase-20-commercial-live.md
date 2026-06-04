# Phase 20 S6 — commercial_viral 라이브 검증 (실 LLM)

> 2026-06-04 | 실 LLM 1회(planning gpt-4o-mini) + 1회(critic gpt-4o) | OUTPUT_MODE=commercial_viral
> 입력: "동네 카페가 신메뉴(흑임자 라떼) 런칭하는 30초 쇼츠 기획"
> 스크립트: Temp/run_commercial_verify.py (레포 밖, 커밋 금지) — P-LIVE-VERIFY-001

## 판정: ★ PASS

| # | 검증 | 결과 |
|---|---|---|
| ① | commercial 7슬롯 채움 (market_context/audience_psychology/brand_positioning/commercial_conversion/platform_packaging/production_feasibility/measurement_plan) | ✅ 7/7 전부 채워짐 |
| ② | scene 상업 2필드 (brand_signal/commercial_signal) | ✅ 2씬 모두 채워짐 |
| ③ | ★ 보장 표현 금지 (보정1) — "100만/조회수 보장/무조건/반드시 터/viral 보장" | ✅ 검출 0 (clean) |
| ④ | ★ 추정 표기 (보정3) — market/audience 실데이터 없으면 "추정:" | ✅ market_context·audience_psychology 둘 다 "추정:" 시작 |
| ⑤ | compact 직렬화 byte-identical (commercial 키 제외) | ✅ 누수 0 |
| critic | 17차원 채점 (director 10 + 상업 7) | ✅ 17/17, verdict=approve, avg=4.4118 |

## 실측 발췌
```
market_context: "추정: 최근 커피 시장에서 이색 메뉴가 인기를 끌고 있으며, 특히 건강과 웰빙을 고려한 식음료가 각광..."
audience_psychology: "추정: 소비자들은 새로운 맛과 경험을 찾고 있으며, 흑임자는 건강식으로 인식되고 있다."
brand_positioning: "신메뉴 흑임자 라떼를 통해 건강과 맛을 동시에 제공하는 브랜드로 자리매김"
commercial_conversion: "영상 시청 후 카페 방문 유도, 소셜 미디어 공유 촉진"
production_feasibility: "1인 촬영 및 간단한 편집으로 저예산 실행 가능, 대안으로 스마트폰 활용"
measurement_plan: "영상 조회수, 시청 유지율, 소셜 미디어 공유 수, 카페 방문 후 구매율 등"
scene0: brand_signal="브랜드의 따뜻한 이미지 전달" | commercial_signal="신메뉴 홍보와 방문 유도"
critic: 17/17 dims, verdict=approve, avg=4.4118
```

## 결론
- ★ commercial_viral tier 가 **백엔드 end-to-end 라이브 동작**: planning 이 commercial 프롬프트로 10슬롯 + 7필드 scene 채움 → critic 17차원 채점.
- ★ **리스크 보정 3종 실증**: 보장 표현 0(보정1) / 기획 브리프 수준(보정2 — 슬롯 내용이 전략 기획이지 제작물 아님) / market·audience "추정:" 표기(보정3).
- ★ compact byte-identical(누수 0) — gated/additive 보존.
- 비고: Temp 스크립트의 최종 요약 print 줄에 cosmetic 버그(빈 Plan 생성)로 크래시했으나, ①~⑤+critic 실측은 모두 정상 출력. 검증 자체 영향 0.
