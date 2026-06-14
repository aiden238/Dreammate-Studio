# Visual Contract — Orange × Beige Planning Workspace

## 1. 디자인 한 줄 정의

> 따뜻한 종이 위에서 아이디어를 정리하는 학생·기획자용 AI 워크스페이스

HeyGen의 이중 내비 구조, Genspark·Manus의 중앙 집중형 입력 UX, Claude풍 서적 카드를 결합한다.

원본 서비스의 로고·이미지·고유 그래픽은 복제하지 않는다.

---

## 2. 색상 역할

### 기본색 80%

- 아이보리
- 크림 화이트
- 베이지
- 샌드
- 웜그레이
- 짙은 브라운 텍스트

### 강조색 20%

- 앰버
- 오렌지
- 테라코타
- 불꽃 캐릭터의 진홍색

### 핵심 토큰

```css
--color-bg-default: #F5EFE6;
--color-bg-subtle: #EEE3D5;
--color-bg-deep: #E6D6C4;

--color-surface: #FFFAF4;
--color-surface-subtle: #F1E3D4;
--color-surface-pressed: #E7D6C4;

--color-primary: #F47B20;
--color-primary-light: #FFB23F;
--color-primary-hover: #E96818;
--color-primary-pressed: #D94C1A;
--color-primary-disabled: #E8B58E;

--color-text-default: #352A24;
--color-text-muted: #78685F;
--color-text-placeholder: #A08E82;
--color-text-inverse: #FFF9F2;

--color-border-default: rgba(102,72,54,.16);
--color-border-focus: #F47B20;

--color-rail: #573A2A;
--color-rail-text: #E5D7CC;

--color-paper: #FFFAF1;
--color-paper-secondary: #F2E5D3;
--color-paper-ink: #3B2D25;
```

---

## 3. 색상 사용 비율

```text
아이보리·베이지·웜그레이 80%
주황·앰버·테라코타 20%
```

주황은 다음에만 강하게 사용한다.

- 주요 CTA
- 현재 선택
- 진행률
- focus
- 로고
- 핵심 키워드

주황을 장문 본문, 전체 패널 배경, 모든 카드에 사용하지 않는다.

---

## 4. 타이포그래피

### 기획·발표형 제목

```css
font-family:
  "Paperlogy",
  "SUIT Variable",
  "SUIT",
  "Pretendard Variable",
  sans-serif;
```

사용:

- Hero
- 페이지 제목
- 기획안 제목
- 대시보드 주요 수치
- 섹션 제목

### UI와 본문

```css
font-family:
  "SUIT Variable",
  "SUIT",
  "Pretendard Variable",
  "Pretendard",
  system-ui,
  sans-serif;
```

사용:

- 버튼
- 입력
- 사이드바
- 카드 설명
- 보조 정보
- 상태 문구

### 서적·대본

```css
font-family:
  "Noto Serif KR",
  "MaruBuri",
  "Nanum Myeongjo",
  serif;
```

사용:

- 최종 대본
- 긴 인용문
- 방향 요약의 책 페이지 본문

작은 UI 텍스트에는 사용하지 않는다.

---

## 5. 레이아웃

### 데스크톱

```text
Primary Rail 72–76px
+ Secondary Sidebar 220–260px
+ Main Canvas minmax(0, 1fr)
```

Primary Rail:

- 홈
- 기획
- 브랜드
- 결과
- Brain

Secondary Sidebar:

- 현재 영역의 하위 메뉴
- 현재 프로젝트/브랜드
- Brand Memory 요약

Main Canvas:

- breadcrumb / actions
- page title
- main task
- context panel

### 모바일

- 두 사이드바 제거
- 하단 탭바 사용
- 주요 CTA는 화면 하단 safe area 고려
- 한 화면 한 주요 행동
- 카드 1열
- 44px 이상 터치 영역

---

## 6. 카드

### 일반 패널

- 크림 화이트
- 얇은 브라운 테두리
- 낮은 그림자
- radius 16–22px

### 서적 카드

- 아이보리 종이 질감
- Paperlogy 제목
- Noto Serif KR 긴 문장
- 주황 광원은 약하게
- 콘텐츠 가독성 우선

### 선택 카드

- 주황 테두리
- 매우 옅은 앰버 배경
- 체크 아이콘 + 텍스트
- 색상만으로 선택을 표현하지 않음

---

## 7. CTA

Primary:

```text
#FFB23F → #F47B20 → #D94C1A
```

- 진한 브라운 텍스트
- 한 화면 하나
- disabled, loading, focus 상태 필수

Secondary:

- 투명 또는 크림 배경
- 얇은 웜 브라운 테두리
- hover에서 매우 옅은 주황

---

## 8. 금지

- 화면 전체를 주황색으로 채우기
- 모든 카드에 그라데이션
- 장문 주황 텍스트
- 시각 레퍼런스의 목업 데이터를 제품에 하드코딩
- 원본 HeyGen·Genspark·Manus UI의 고유 자산 복제
- 글꼴 세 종류를 같은 문단 안에서 혼용
- 대비가 약한 베이지 텍스트
