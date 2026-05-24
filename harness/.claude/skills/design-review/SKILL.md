---
name: design-review
description: |
  apps/web/design.md 기준으로 프론트엔드 설계와 구현을 검토할 때 사용한다.
  모바일 우선, 카드 단위 결과, 한 줄 방향 승인 UX, 30–60초 생성 대기 UX,
  영상 제작 UI 미포함, Intent Filtering, Project Memory 등 design.md의
  모든 핵심 규칙을 점검한다. design_review_checklist.md 흡수.
  키워드: "design 검토", "디자인 리뷰", "design review", "UX 점검",
  "프론트 설계", "design.md 점검", "화면 설계 검토".
applies_to: [claude]
phase: [all]
related_contracts:
  - apps/web/design.md
  - docs/contracts/mvp_non_goals.md
related_state: []
version: v1.0.0
---

# design-review

design.md의 규칙은 많고 까먹기 쉽다. 새 화면, 새 컴포넌트, design 변경 제안이 들어올 때마다 이 절차로 점검한다.

## 트리거 조건

- 새 화면 / 컴포넌트 추가 시
- design.md 변경 제안 시 (contract-change 동반)
- Phase 종료 직전 (프론트 작업이 포함된 Phase)
- 사용자가 "디자인 한 번 보자", "UX 검토해줘"
- 외부 디자인 시안이 들어왔을 때

## 점검 체크리스트

### 1. 신규 사용자 진입 (15초 룰)

- [ ] 첫 화면에서 무엇을 해야 할지 1초 안에 보이는가?
- [ ] 신규 회원은 Discovery onboarding으로 자동 진입하는가?
- [ ] Brand 없는 상태에서 새 영상 만들기 시도 시 Discovery로 분기되는가?
- [ ] Mode trigger 규칙(design.md §5)이 코드에 명확히 구현됐는가?

### 2. Discovery Mode (Track A)

- [ ] 단계가 7개 이하인가?
- [ ] 단계당 카드가 정확히 5장(또는 의미 있는 4장 미만)인가?
- [ ] 각 카드에 이름 / 설명 / 적합 상황 / 장점 / 주의점 5개 필드가 있는가?
- [ ] "직접 입력" 옵션이 5장 아래에 항상 있는가?
- [ ] 단계별 진행률(3/6 같은)이 상단에 표시되는가?
- [ ] "이전 단계" 버튼이 항상 있는가?
- [ ] 카드 5장이 서로 충분히 구별되는가? (의미적 중첩 30% 미만)
- [ ] 광고적 표현 ("최고의", "혁신적인")이 카드 텍스트에 없는가?

### 3. Quick Mode (Track B)

- [ ] 짧은 프롬프트 (10–200자) 입력 가능?
- [ ] 부족정보 질문이 최대 2개로 제한되는가?
- [ ] 한 줄 방향 카드에 인라인 편집이 가능한가?
- [ ] 승인/수정/다시 좁히기 3-way가 있는가?
- [ ] Brand/Domain/Series 컨텍스트가 메모리에서 자동 상속되는가?

### 4. 4계층 표현

- [ ] 사용자에게 "Brand/Domain/Series" 용어를 직접 노출 안 하는가?
- [ ] 좌측 네비 또는 breadcrumb으로 계층 경로가 보이는가?
- [ ] 같은 Series 안에서 영상 추가 시 Quick Mode 자동 분기?
- [ ] 새 Series 만들 때 Series 카드 단계만 거치는가?

### 5. AI 생성 결과 표시

- [ ] 3개 기획안이 비교 가능한 카드로 표시되는가?
- [ ] 각 plan 카드에 이름/콘셉트/후킹/흐름/장점/리스크가 있는가?
- [ ] 영상 구성안이 타임라인 형태로 표시되는가?
- [ ] 후킹 후보 3개가 별도 카드로 보이는가?
- [ ] 품질 평가가 점수+이유+개선안 세트로 제공되는가?
- [ ] 긴 문단이 카드 단위로 분할되는가?

### 6. 생성 대기 UX (30–60초)

- [ ] 빈 로딩 스피너만 노출하지 않는가?
- [ ] 4단계 진행률 스테퍼(Intent/RAG/Plan/Critic)가 보이는가?
- [ ] 부분 결과가 즉시 노출되는가?
- [ ] 백그라운드 허용 + 완료 시 토스트 알림 있는가?
- [ ] 취소 버튼이 항상 있는가? 취소해도 부분 결과 보존되는가?

### 7. State / Error 처리

design.md §20의 필수 상태 모두 구현됐는지:

- [ ] Empty State
- [ ] Loading State
- [ ] Streaming State
- [ ] Partial Result State
- [ ] Error State (다음 액션 제시)
- [ ] Retry State
- [ ] Save Success State
- [ ] Memory Updated State

- [ ] 오류 시 "오류 발생" 만 표시 안 하고 다음 행동 제시하는가?
- [ ] 부분 결과 있으면 삭제 안 하고 보존하는가?
- [ ] 네트워크 끊김 시 로컬 임시 저장 후 재연결 자동 동기화?

### 8. Intent Filtering

- [ ] 영상기획 외 입력 시 IntentWarningBox 표시?
- [ ] 거부 톤이 아니라 안내 톤인가?
- [ ] "콘텐츠 방향으로 정리" 버튼이 있는가?
- [ ] 영상기획 외 입력이 Project Memory에 저장 안 되는가?

### 9. Project Memory

- [ ] Brand Memory가 좌측에 접혀 있는가?
- [ ] 사용자가 펼쳐서 항목별 확인/수정 가능?
- [ ] Quick Mode에서 Brand Memory 자동 prompt 주입?
- [ ] 자동 반영 시 사용자에게 짧은 안내가 표시되는가?
- [ ] 거절 이유, 수정 요청도 함께 저장되는가?

### 10. 모바일 한 손 조작

- [ ] 360–430px 세로 스크롤 우선?
- [ ] 한 화면 한 주요 CTA?
- [ ] 주요 CTA가 하단 고정(BottomActionBar)?
- [ ] 카드 간 간격 16px 이상?
- [ ] 하단 CTA 높이 56px 이상?
- [ ] 터치 영역 44×44px 이상?

### 11. 접근성

- [ ] 색상만으로 상태 구분 안 하는가?
- [ ] 폼 입력에 라벨 항상?
- [ ] 키보드 탐색 가능?
- [ ] 카드 제목 h2/h3 일관?
- [ ] 진행률에 aria-current?

### 12. MVP 범위 위반

design.md §8 MVP 제외 항목 확인:

- [ ] 영상 제작 / 편집 UI 없는가?
- [ ] 자동 업로드 UI 없는가?
- [ ] Billing 화면 없는가?
- [ ] Team Workspace 없는가?
- [ ] Admin Dashboard 없는가?
- [ ] Expo / 네이티브 분기 코드 없는가?

위반 발견 시 즉시 fail. contract-change 또는 제거.

### 13. 시각 스타일

- [ ] shadcn/ui + Tailwind 사용?
- [ ] 광고적 / 과도하게 화려한 톤 아닌가?
- [ ] 강조색이 CTA, 선택 상태, 점수 시각화에만 제한적?
- [ ] 본문 폰트 모바일 15–16px?
- [ ] 카드 제목 17–19px?
- [ ] lucide-react 아이콘만 사용?

## 절차

### 1. 점검 대상 식별

- 신규 화면/컴포넌트의 경로
- 변경된 design.md 섹션
- 영향 받는 영역

### 2. 위 13 카테고리 순차 점검

각 항목 pass/fail/skip 기록. 점검 도중 발견된 추가 위반도 메모.

### 3. 결과 기록

`eval/design_reviews/{trigger}-{YYYY-MM-DD-HHMM}.md`:

```markdown
# Design Review

- 대상: {화면 또는 컴포넌트 이름}
- 트리거: {새 화면 / Phase 종료 / 변경 제안}
- 검토자: {claude / user}
- 결과: {ALL PASS / N FAIL}

## 카테고리별 결과
{13개 표}

## 위반 항목
{있다면 나열, 각각의 영향}

## 권장 수정
{우선순위 순}

## 결정
- 진행 가능 / fix 후 재검토 / contract-change 필요
```

### 4. 위반 처리

```
MVP 범위 위반 (카테고리 12) → 무조건 차단
사용자 진입 / 핵심 흐름 위반 (1, 2, 3) → 차단
상태/에러 처리 누락 (7)        → 차단
모바일 한 손 조작 위반 (10)    → 사용자 결정 (모바일 비중에 따라)
접근성 위반 (11)               → fix 필요
시각 스타일 (13)               → 권장, 차단 안 함
```

## 자주 발생하는 실수

1. **체크리스트 형식적 통과**: "한 손 조작 가능?" → 실제 모바일에서 안 봄.
2. **MVP 범위 점검 생략**: "이미 만들어 둔 거 살리자" 식으로 영상 편집 UI가 슬며시.
3. **30–60초 대기 UX 빈 스피너**: 사용자가 이탈하는 가장 큰 원인.
4. **State 일부만 구현**: "에러 상태는 나중에"가 운영까지 감.
5. **Intent Filter 거부 톤**: 사용자가 거절당한 느낌 받음. 안내 톤이어야 함.
6. **모바일 360px 미점검**: Galaxy S22에서 깨짐 발견.

## 다른 Skill과의 관계

```
contract-change   : design.md 변경 시 선행
qa-check          : 카테고리 3, 4 일부 중복 점검
multi-llm-validation : 큰 디자인 결정은 다른 모델로 교차 검토
phase-complete    : 프론트 Phase 종료 시 자동 호출
```

## 종료 조건

- 모든 카테고리 pass → 진행 OK
- 일부 fail + 우선순위 결정 → 결정 기록 후 종료
- MVP 위반 → 차단, contract-change 또는 제거 작업으로 위임 후 종료
