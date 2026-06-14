# Page Mapping — Reference → Existing Routes

## 1. 홈

### 레퍼런스

- `reference/index.html`

### 실제

- `app/page.tsx`

### 적용

- 중앙 Hero
- 큰 아이디어 입력
- 빠른 시작 상황 버튼
- 하단 시작 카드
- Brain 진입

### 유지

- `startPlan`
- 이미지 첨부
- 입력 검증
- ProgressStepper
- ErrorCard
- 기존 4가지 상황 route

---

## 2. 프로젝트 대시보드

### 레퍼런스

- `reference/dashboard.html`

### 실제

현재 구현된 route와 데이터 상태를 먼저 확인한다.

대시보드가 독립 route로 없으면:

- 새 route를 임의 생성하지 않는다.
- 홈·Brain·브랜드 구조 안에서 기존 기능을 우선 배치한다.
- route 추가는 active Phase 승인 후 한다.

---

## 3. 브랜딩·Discovery

### 레퍼런스

- `reference/discovery.html`
- `reference/direction-summary.html`

### 실제

- `app/new/branding/page.tsx`
- `app/new/discovery/step/[step]/page.tsx`
- 관련 Discovery 컴포넌트
- Quick 방향 승인 화면

### 적용

- 진행률
- 질문 제목
- 2열 선택 카드
- 우측 현재 방향 요약
- 모바일에서는 현재 방향을 상단 접기 패널로 전환
- 방향 요약은 책 페이지 느낌

### 유지

- LLM 질문 흐름
- 직접 입력
- 이전/다음
- 자유 입력
- 생성 route
- 고정 하단 CTA

---

## 4. 생성 진행

### 레퍼런스

- `reference/generation.html`

### 실제

- `/plan/[plan_id]`의 loading branch
- `ProgressStepper`
- SSE progress wrapper

### 적용

- 단계별 진행
- 부분 결과
- 백그라운드 안내
- 빈 spinner 금지

### 유지

- 실제 SSE event
- ErrorCard
- 재시도
- 부분 결과 보존

---

## 5. 기획안 비교

### 레퍼런스

- `reference/workspace.html`

### 실제

- `app/plan/[plan_id]/page.tsx`
- `components/PlanCard.tsx`
- 선택·피드백 wrapper

### 적용

- 데스크톱 3열 비교
- 모바일 1열
- 우측 Brand Memory
- 평가 점수
- 선택/수정/거절 행동

### 유지

- `generateMultiPlan`
- `getPlan`
- `selectPlan`
- `sendFeedback`
- sessionStorage 선택 복원
- SSE progress
- Brain reflected 배너
- reject reason
- AuthGuard

### 보호

`PlanCard.tsx`는 우선 수정하지 않는다. 외부 wrapper로 시각 구조를 만든다.

---

## 6. 최종 결과

### 레퍼런스

- `reference/final-output.html`

### 실제

현재 결과 페이지의 실제 구조를 audit한 뒤 기존 데이터로 구성한다.

### 적용

- 좌측 결과 섹션 내비
- 기획 요약
- 대본
- 컷 구성
- 촬영 체크리스트
- 업로드 문구

### 주의

API가 제공하지 않는 데이터를 목업으로 채우지 않는다.

존재하지 않는 출력은:

- 숨기기
- 준비 중 표시
- 기존 output schema 기반으로 graceful 처리

---

## 7. Brain

### 레퍼런스

- `reference/brain.html`

### 실제

- `app/brain/page.tsx`
- `components/brain/PkmGraph.tsx`

### 적용

- 메모리 카드
- 최근 결정 로그
- 그래프와 카드 전환
- 따뜻한 카드 배경

### 유지

- 실제 PKM API
- 소유권
- 잠금·편집·삭제
- no-data state
- graph lazy load
- 모바일 카드 모드

---

## 8. 레퍼런스 보드

### 레퍼런스

- `reference/references.html`

### 실제

현재 별도 route가 없다면 구현하지 않는다.

멀티모달 이미지 첨부와 기존 PKM 흐름 안에서 레퍼런스 경험을 개선한다.
새 route는 별도 승인 범위다.
