# product_boundary.md

> ⚠️ **PLACEHOLDER** — 본 contract는 부분적으로 채워진 상태.
> Phase 0에서는 MVP 경계의 핵심 원칙만 명시. 정식 contract는 Phase 5+ MVP 출시 시점에 갱신.

## Status

```yaml
status: placeholder
fill_in_phase: 5+
priority: low
estimated_final_lines: 150
last_updated: 2026-05-26
```

## Why Placeholder?

본 contract의 핵심 결정("영상기획 AI, 영상 제작 AI 아님")은 이미 `00_START_HERE.md`, `CLAUDE.md`, `AGENTS.md`, `product/vision.md`, `mvp_non_goals.md`에 명시되어 운영 중. 정식 contract 형태로 깊이 채우는 시점은 Phase 5+ (MVP 출시 직전) 또는 외부 사용자 onboarding 첫 설계 시점.

## Scope (TBD)

본 contract가 다룰 범위:

- MVP 핵심 흐름 명시:
    - Discovery Wizard 5단계 + Quick Mode
    - 4계층 데이터 모델 (User → Brand → Domain → Series → Video Project)
    - MOA Lite (Intent → Planner → Critic[max revise 2] → Rewriter)
    - RAG Lite 5단계 승격
- MVP에 영구 포함 (이 범위 안에서 깊이 발전):
    - 영상기획안 3개 생성 + Critic 평가
    - Brand Memory 자동 추출
    - 한국어 UX 친화 (광고 표현 차단, 친근체)
- MVP에 영구 제외 (mvp_non_goals.md와 정합):
    - 영상 자동 편집 / TTS / BGM 생성 / 자막 합성
    - 자동 업로드 (YouTube / Instagram)
    - 결제 / 팀 협업 (Phase 11+ 검토)
    - Expo 모바일 / Spring Boot 백엔드 분리 (Phase 21+ 검토)
- 확장 후보 (MVP 안정 후):
    - 영상 분석 도구 (외부 API 연동)
    - 영상 미리보기 (스토리보드 → 시뮬레이션)
    - Phase 11+ 결제 / paid tier
- 경계 변경 절차 (contract-change Skill 통과 의무)
- "영상 제작 기능" 도입 제안에 대한 기본 응답 (거절, Phase 21+ 재검토)

## Known Dependencies (when filled in)

외부 표준:
- 해당 없음 (제품 정의)

내부 의존 파일:
- `product/vision.md`
- `product/positioning.md`
- `product/mvp_scope.md`
- `product/user_scenarios.md`
- `docs/contracts/mvp_non_goals.md`
- `00_START_HERE.md`, `CLAUDE.md`, `AGENTS.md`
- `PROJECT_STATE.md` (제품 정의 25 결정 핵심)
- `phases/active/*/` (현재 Phase의 범위)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 5+ 진입 (MVP 출시 직전)
- 또는 첫 외부 onboarding 흐름 설계 시점
- 또는 MVP 범위 변경 제안 발생 시 (mvp_scope.md 변경 시 동시 갱신)
- 또는 phase-review Skill에서 경계 점검 요청 발생 시

## Related Skill / Phase

- Skill: `phase-review`, `qa-check` (카테고리 1: 제품 범위)
- Phase: 5+
- 책임자: AI(초안) + 사용자(최종 결정자)
