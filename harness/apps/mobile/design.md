# mobile/design.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 21+
priority: low
estimated_final_lines: 200
last_updated: 2026-05-26
```

## Why Placeholder?

MVP는 PWA(Progressive Web App)로 충분하다. Phase 1-20 동안 모바일 네이티브
진입 결정은 보류이며, Phase 21 진입 결정 이후 웹 design.md와 토큰 공유
전략을 수립한 뒤 작성한다.

## Scope (TBD)

본 파일이 다룰 범위:
- Expo React Native 기반 디자인 시스템 (컴포넌트 라이브러리)
- `apps/web/design.md`와 디자인 토큰 공유 전략 (색상, 타이포, 간격)
- 네이티브 특화 UX 패턴 (스와이프, 햅틱, 네이티브 내비게이션)
- iOS / Android 플랫폼별 디자인 차이 가이드
- 다크모드 / 라이트모드 지원 방식
- 영상기획 핵심 흐름의 모바일 UX 재해석 (Discovery Wizard 모바일 버전)
- Expo EAS Build 기반 스토어 배포 스크린샷 가이드

## Known Dependencies (when filled in)

- `apps/web/design.md` — 웹 디자인 시스템 (토큰 공유 소스)
- `docs/contracts/frontend_design_contract.md` — 디자인 계약 (공통 부분)
- `docs/decisions/mobile_strategy.md` — 모바일 전환 전략 결정
- `apps/mobile/README.md` — 앱 구조 및 셋업
- `packages/shared-types/README.md` — 공유 타입 (컴포넌트 props 포함)
- Expo SDK (버전 Phase 21 시점 확정)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 21 모바일 네이티브 진입 결정 (docs/decisions/mobile_strategy.md에 기록)
- `apps/web/design.md` 안정화 완료 (토큰 추출 가능 상태)

## 예시 토큰 공유 형식 (fill-in 시 참고)

```typescript
// 웹/모바일 공유 디자인 토큰 예시
export const tokens = {
  colors: {
    primary: '#7C3AED',
    surface: '#F8F7FF',
  },
  spacing: { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 },
  fontSize: { sm: 12, md: 14, lg: 16, xl: 20, xxl: 24 },
};
```

## Related Skill / Phase

- Skill: design-review
- Phase: 21+
- 책임자: 운영자 / AI
