# Phase 30 — UI 리브랜딩 (Orange × Beige) · goals

## 목표
현재 앱의 기능(API/SSE/Auth/PKM/피드백/route/타입)을 **100% 보존**하면서 시각 체계를
indigo(#6366F1)/cyan → **따뜻한 주황(#F47B20) × 아이보리·베이지 "종이 워크스페이스"**로 재구성.
> 출처: `apps/web/design_reference/` (Claude Code UI Handoff v1, **사용자 채택 2026-06-15**).

## 사용자 결정 (2026-06-15)
- **리브랜딩 채택** + 데스크톱 이중 내비(Primary Rail + Secondary Sidebar) 포함.
- **final-output = 브리프 깊이로 제한** — 현 output_schema(hook/beats/scene_breakdown) 범위 내만.
  '대본/촬영 체크리스트' 슬롯은 **존재 데이터만**, 없으면 숨김/준비중 (제품 경계 = 영상기획 브리프, **제작 아님**).

## 핵심 원칙 (핸드오프 CLAUDE.md + 프로젝트 규율)
- **behavior-preserving**: 토큰·레이아웃·정보계층만. API/output_schema/DB/AI flow **불변**.
- **legacy scale de-risk**: `primary-N00` 75 + `neutral-N00` 182 + status 68 = **~325건** 직접 사용(audit) →
  Slice 1에서 `tailwind.config` scale 값 자체를 웜 팔레트로 재매핑 → 컴포넌트 개별 편집 최소로 자동 리컬러.
- **PlanCard 내부 무수정**(wrapper만). **HIDDEN_PREFIXES** 보존. 모바일 하단탭 유지.
- 충돌 우선순위: API/보안/접근성 > 동작/테스트 > 시각.

## Baseline (Slice 0 audit, 2026-06-15)
tsc 0 / lint 0 / 13 routes. HEAD af345ae 후속(1e7e053).
