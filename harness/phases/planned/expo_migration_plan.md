# expo_migration_plan.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 21+
priority: low
estimated_final_lines: 160
last_updated: 2026-05-26
```

## Why Placeholder?

PWA로 MVP를 운영하는 Phase 1-20 동안 모바일 네이티브 전환 결정은 보류한다.
모바일 사용자 비중 또는 사용자 요구 강도가 임계를 초과할 때 작성 착수한다.

## Scope (TBD)

본 파일이 다룰 범위:
- PWA → Expo React Native 마이그레이션 전체 계획
- 코드 재사용 전략 (비즈니스 로직, API 클라이언트, 타입 공유)
- `apps/mobile/design.md` 디자인 시스템 공유 방식 (토큰 기반)
- 앱스토어 배포 자동화 (EAS Build + EAS Submit)
- PWA 사용자 → 네이티브 앱 마이그레이션 (데이터 연속성 보장)
- 기능 동등성 체크리스트 (PWA 기능 100% → 네이티브 완성 기준)
- 롤아웃 전략 (PWA 병행 운영 기간, 점진 전환)

## Known Dependencies (when filled in)

- `docs/decisions/mobile_strategy.md` — 모바일 전환 결정 기록
- `apps/mobile/design.md` — 모바일 디자인 시스템
- `apps/mobile/README.md` — 모바일 앱 구조
- `apps/web/design.md` — 웹 디자인 시스템 (공유 소스)
- `packages/shared-types/README.md` — 공유 타입
- `packages/api-client/README.md` — API 클라이언트 (재사용)
- Expo SDK, EAS Build (Phase 21 시점 버전 확정)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- 모바일 기기 사용자 비중 70% 도달 (3개월 평균)
- 또는 모바일 네이티브 기능 요구 (Push 알림, 오프라인 등) 사용자 요청 강도 임계 초과

## 예시 마이그레이션 체크리스트 형식 (fill-in 시 참고)

```
## 기능 동등성 체크리스트

- [ ] 로그인 / 회원가입 (OAuth 포함)
- [ ] Discovery Wizard 전체 흐름
- [ ] Quick Mode 전체 흐름
- [ ] 기획안 조회 / 수정 / 저장
- [ ] 피드백 입력
- [ ] 알림 (PWA Push → 네이티브 Push)
```

## Related Skill / Phase

- Skill: design-review
- Phase: 21+
- 책임자: 운영자
