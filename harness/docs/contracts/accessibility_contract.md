# accessibility_contract.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 5+
priority: high
estimated_final_lines: 250
last_updated: 2026-05-26
```

## Why Placeholder?

MVP Phase 0~4에서는 핵심 흐름(Discovery/Quick + 카드 + 생성) 구현이 우선. PWA 출시 또는 첫 외부 사용자 평가 시점에 a11y 표준을 정량 검증 가능한 형태로 고정한다. 그 전까지는 `frontend_design_contract.md` §5 (a11y) 기본 가이드만으로 충분.

## Scope (TBD)

본 contract가 다룰 범위:

- WCAG 2.1 AA 준수 검증 절차 (자동 + 수동)
- 색상 대비 최소 4.5:1 (텍스트), 3:1 (UI 컴포넌트)
- 키보드 네비게이션 표준 (Tab 순서, focus visible, 단축키)
- 스크린 리더 호환성 (NVDA / VoiceOver / TalkBack 테스트)
- 모션 감소 (`prefers-reduced-motion`) 대응
- alt text / aria-label 작성 가이드
- ARIA 역할 / 상태 / 속성 표준 사용
- 폼 라벨 / 에러 메시지 a11y
- 카드 5장 그리드 + 직접 입력 슬롯의 키보드 흐름
- 4단계 progress stepper의 스크린 리더 안내 (aria-live)
- SSE/polling 진행률 업데이트의 스크린 리더 알림
- 모바일 a11y (터치 타겟 44×44, 줌 허용)
- 다국어 a11y (Phase 11+)

## Known Dependencies (when filled in)

외부 표준:
- WCAG 2.1 AA (W3C)
- WAI-ARIA 1.2
- KISA 웹 접근성 지침 (한국)
- 모바일 a11y: Apple HIG, Android Material a11y

내부 의존 contract:
- `frontend_design_contract.md` §5 (a11y 기본 가이드, 이미 정의)
- `apps/web/design.md` §20 (Error UX), §22 (Progress Stepper)
- `apps/web/component_map.md` (카드 / stepper / 폼)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 5+ 진입 (PWA MVP 출시 시점)
- 또는 첫 외부 사용자 평가 시점
- 또는 a11y 관련 사용자 피드백 누적 3건 이상

## Related Skill / Phase

- Skill: `design-review`, `qa-check` (a11y 항목 카테고리)
- Phase: 5+
- 책임자: AI(초안) + 사용자(검토) + 외부 a11y 자문(Phase 11+)
