# apps/mobile

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

Phase 1-20은 PWA 중심으로 운영된다. 모바일 네이티브 앱은 사용자 구성비 및
사용 패턴 데이터가 축적된 Phase 21 이후에 진입 여부를 결정한다.

## Scope (TBD)

본 파일이 다룰 범위:
- Expo React Native 앱 전체 폴더 구조 설명
- Expo SDK 버전 및 의존성 설정 방법
- iOS / Android 빌드 환경 설정 (Expo EAS Build)
- `apps/mobile/design.md` 디자인 시스템 적용 방법
- `packages/shared-types`와 `packages/api-client` 연동 방법
- App Store / Google Play 배포 자동화 flow
- PWA → 네이티브 앱 데이터 마이그레이션 전략

## Known Dependencies (when filled in)

- `apps/mobile/design.md` — 모바일 디자인 시스템
- `docs/contracts/tech_stack_contract.md` — 기술 스택 (Expo 버전 포함)
- `docs/decisions/mobile_strategy.md` — 진입 결정 기록
- `phases/planned/expo_migration_plan.md` — PWA → Expo 마이그레이션 계획
- `packages/api-client/README.md` — API 클라이언트 연동
- Expo EAS Build, App Store Connect, Google Play Console

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 21 진입 결정 (PHASE_REGISTRY.md에 Phase 21 active 등록)
- `docs/decisions/mobile_strategy.md` 작성 완료

## 예시 폴더 구조 (fill-in 시 참고)

```
apps/mobile/
├── app/                  # Expo Router 기반 화면
│   ├── (tabs)/           # 탭 내비게이션
│   └── plan/[id].tsx     # 기획안 상세
├── components/           # 네이티브 컴포넌트
├── hooks/                # 커스텀 훅
├── app.json              # Expo 설정
└── eas.json              # EAS Build 설정
```

## Related Skill / Phase

- Skill: N/A
- Phase: 21+
- 책임자: 운영자 / AI
