# pwa_mvp_plan.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: high
estimated_final_lines: 200
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 1 세부 계획은 phase-start Skill로 Phase 1 진입 시점에 product/roadmap.md,
product/mvp_scope.md를 기반으로 상세 작성한다. 현재는 스코프 보존 목적으로만 유지한다.

## Scope (TBD)

본 파일이 다룰 범위:
- PWA 기반 MVP 출시 전체 계획 (Phase 1 ~ Phase 10 로드맵)
- 사용자 100명 유치 목표 달성 전략 (채널, 온보딩, 리텐션)
- 영상기획 핵심 흐름 완성 기준 (Discovery Wizard + Quick Mode)
- Phase별 출시 기준 (phase-complete Skill 체크리스트 연계)
- 기술 스택 선택 근거 (PWA 우선 이유, 네이티브 앱 유보 이유)
- 주요 마일스톤 및 일정 (Phase 1-10 각 Phase 예상 기간)
- 리스크 및 대응 계획 (LLM 비용, RAG 품질, 사용자 이탈)

## Known Dependencies (when filled in)

- `product/mvp_scope.md` — MVP 기능 범위 원천
- `product/roadmap.md` — Phase별 로드맵
- `PHASE_REGISTRY.md` — Phase 진행 현황 추적
- `docs/contracts/product_boundary.md` — 제품 경계 (영상 제작 포함 금지 등)
- `docs/contracts/mvp_non_goals.md` — MVP 제외 기능 목록
- `phase-start` Skill — Phase 진입 시 본 파일 상세화
- `phase-complete` Skill — Phase 완료 체크리스트 연계

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- phase-start Skill로 Phase 1 공식 진입
- `product/mvp_scope.md`와 `product/roadmap.md` 최신 버전 확정

## 예시 마일스톤 형식 (fill-in 시 참고)

```
| Phase | 목표 | 출시 기준 | 예상 기간 |
|-------|------|-----------|-----------|
| 1     | API + MOA Lite MVP | 핵심 흐름 완성, 사용자 10명 | 4주 |
| 2     | RAG 통합 | RAG 검색 품질 60% 이상 | 3주 |
| 3     | 사용자 계정 | 회원가입/로그인 완성 | 2주 |
```

## Related Skill / Phase

- Skill: phase-start, phase-complete, phase-review
- Phase: 1+
- 책임자: 운영자 / AI
