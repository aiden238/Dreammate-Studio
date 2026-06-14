# Page Reference Map

## 핵심 사용자 흐름

```text
index.html
→ discovery.html
→ direction-summary.html
→ generation.html
→ workspace.html
→ final-output.html
→ brain.html
```

## 보조 흐름

```text
dashboard.html
├── 기존 프로젝트 → workspace.html
├── 완료 프로젝트 → final-output.html
└── 신규 프로젝트 → discovery.html

references.html
├── 직접 레퍼런스 추가
├── AI 레퍼런스 탐색
└── 브랜드 방향·기획 생성에 선택 반영
```

## 구현 우선순위

1. `discovery.html`
2. `workspace.html`
3. `final-output.html`
4. `dashboard.html`
5. `brain.html`
6. `references.html`
7. `generation.html`
8. `direction-summary.html`

## 하네스 우선순위

실제 화면 시각 구현 시:

1. 본 HTML 레퍼런스
2. visual rules
3. component contract
4. 기존 design.md
5. tokens.md

기능·접근성·데이터 계약 충돌 시 기존 contract가 우선합니다.
