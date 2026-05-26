# mobile_strategy.md — 모바일 전략 (ADR)

> 위치: `docs/decisions/mobile_strategy.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/tech_stack_contract.md` §2.1, §4 (Phase 21+ Expo)
> 참조: `docs/decisions/frontend_design_strategy.md`, `product/target_users.md`

---

## 0. 결정 요약

```
MVP (Phase 1~10):
- Next.js 14 PWA (next-pwa)
- 모바일 우선 디자인
- 네이티브 앱 미구현

Phase 11~20:
- 모바일 PWA UX 강화 (Phase 11)
- 오프라인 제한 지원 검토 (Phase 13+)
- 모바일 첫 사용자 비중 70% 도달 시 우선 강화

Phase 21~30:
- Expo React Native 네이티브 앱 (Phase 24)
- iOS / Android 출시
- PWA + Native 양쪽 운영
```

---

## 1. MVP는 PWA로 (Phase 1~10)

### 1.1 선택 이유

```
1. 빠른 출시
   - Next.js PWA는 코드 1개로 모바일 + 데스크탑 지원
   - 별도 앱 개발 / 심사 / 출시 시간 절약

2. 1인 운영 친화
   - 앱 스토어 심사 / 업데이트 부담 없음
   - 같은 코드 베이스 (FE 통일)
   - hotfix 즉시 배포

3. iOS / Android 동시 지원
   - PWA는 모든 모바일 브라우저 지원
   - 사용자 별도 설치 부담 적음 ("홈 화면에 추가")

4. 핵심 가치는 기획 결과
   - 영상기획 결과가 핵심 가치 → 네이티브 기능 의존 적음
   - 카메라 / 알림 / 백그라운드 작업 등 비핵심
```

### 1.2 PWA 한계 (인정)

```
- iOS Safari의 PWA 지원이 Android보다 약함 (push notification 제한 등)
- 앱 스토어 노출 없음 (마케팅 채널 1개 부족)
- 사용자 인식 "앱" vs "웹사이트" 차이 (가치 인식)
```

### 1.3 next-pwa 사용

```
- next-pwa 설정으로 manifest.json + service worker 자동
- "홈 화면에 추가" 가능
- offline은 미지원 (MVP)
- icon / splash screen 디자인 (Phase 3)
```

---

## 2. Phase 11+ 모바일 우선 강화

### 2.1 Phase 11 작업 항목

```
1. 모바일 UX 정밀화
   - 터치 최적화 (44px 이상 tap target)
   - 스와이프 카드 (Discovery 5장 카드 좌우 스와이프)
   - bottom navigation (모바일 우선)
   - 하단 fixed CTA 버튼

2. 반응형 정교화
   - 375px (iPhone SE) ~ 414px (iPhone Pro Max) 정밀 디자인
   - 768px (태블릿) 별도 디자인
   - 1024px+ 데스크탑 보조

3. PWA UX 강화
   - splash screen 디자인
   - 앱 아이콘 (iOS / Android)
   - "홈 화면 추가" 유도 (smart banner)
```

### 2.2 Phase 13+ 오프라인 제한 지원

```
오프라인 캐시 대상:
- 이전 영상 기획 결과 (읽기 전용)
- Brand Memory (읽기 전용)

오프라인 미지원 (영구):
- 새 영상기획 생성 (LLM 호출 필요)
- 모든 mutation (저장 / 수정)

이유:
- LLM 호출은 네트워크 필수
- 오프라인 mutation 동기화는 복잡 + 위험
```

---

## 3. Phase 21+ Expo React Native (Phase 24)

### 3.1 진입 트리거

```
다음 중 하나 이상 충족 시 진입.

1. 사용자 모바일 비중 70% 이상
2. PWA 한계로 인한 사용자 이탈 시그널
3. push notification 필수 요구 발생
4. 네이티브 기능 (카메라 / 공유 / 저장) 요구 발생
5. 앱 스토어 노출이 마케팅 채널로 필요
```

### 3.2 Expo 선택 이유 (Phase 24 진입 시)

```
1. React Native 표준 (한국 시장 친화)
2. 빌드 인프라 통합 (EAS Build)
3. OTA (Over-The-Air) 업데이트 (앱 스토어 심사 우회 가능)
4. Next.js와 컴포넌트 공유 가능 (Solito 또는 직접 분리)
5. iOS / Android 동시 출시

대안 검토:
- Flutter: Dart 학습 곡선 + 한국 인력 풀 적음
- 네이티브 (Swift + Kotlin): 비용 2배
- Capacitor: PWA wrapping (이미 PWA 운영 중이라 가치 적음)
```

### 3.3 PWA + Native 병행 운영

```
Phase 24 진입 후:
- PWA: 데스크탑 사용자 + 가벼운 사용자
- Native: 모바일 헤비 사용자 + paid tier 우대

코드 베이스:
- 공통 비즈니스 로직: shared/ 폴더 (React + RN 호환)
- UI 컴포넌트: 별도 (Web: shadcn/ui, Native: NativeBase 또는 Tamagui)
- 또는 Solito로 통합 (Phase 24 진입 시 검토)

API:
- 동일 backend (FastAPI)
- Native는 별도 인증 흐름 (OAuth deep link)
```

---

## 4. 모바일 UX 핵심 원칙

```
1. 한 화면 = 한 행동
   - 모바일 1 스크롤 안에 핵심 정보 + 1 CTA
   - 모달 / 드로어 적극 사용 (full screen 회피)

2. 카드 단위 결과
   - 영상기획 결과 3개를 카드로 (스와이프 비교)
   - Discovery 5장 카드도 스와이프

3. 한 줄 방향 승인
   - 모바일에서 빠른 결정 UX
   - "이대로 진행" / "다듬기" 2 옵션

4. 30~60초 생성 대기
   - 4단계 progress stepper
   - 부분 결과 즉시 노출
   - 백그라운드 진행 가능 (Phase 13+ Native에서)

5. 광고 표현 차단 + 한국어 친근체
   - 모바일에서 광고적 느낌 더 거슬림
   - 친근체로 부드럽게
```

→ `apps/web/design.md` §22 정합

---

## 5. 측정 지표

```
1. 모바일 사용자 비중
   - 페르소나 1: 50% 목표
   - 페르소나 3: 70% 목표
   - 전체 평균: 60% 목표

2. PWA 설치율
   - 모바일 방문자 중 "홈 화면 추가" 비율
   - 목표: 15% (Phase 11+)

3. 모바일 세션 길이
   - 데스크탑 대비 짧을 것 (자연)
   - 목표: 데스크탑의 70%

4. 모바일 conversion
   - free → paid 전환율 (모바일 vs 데스크탑 비교)
   - Phase 12+ 측정 시작

5. Native 앱 다운로드 (Phase 24+)
   - iOS / Android 별 다운로드 수
   - Native vs PWA 사용자 retention 비교
```

---

## 6. 재검토 트리거

```
1. 모바일 사용자 비중 70% 초과 → Phase 11 모바일 강화 즉시
2. PWA 한계 사용자 피드백 누적 → Native 도입 앞당김
3. iOS PWA 지원 강화 (Apple 정책 변화) → Native 지연 가능
4. push notification 강력 요구 → Native 도입 트리거
5. Phase 21+ 진입 시 → mobile_strategy 전체 재검토
```

---

## 7. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      MVP PWA 선택, Phase 11+ 강화, Phase 24 Expo 진입 트리거,
                      모바일 UX 핵심 원칙, 측정 지표, 재검토 트리거.
```
