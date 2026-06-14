# Dreammate Studio — Claude Code UI Handoff

이 패킷은 완성된 정적 HTML을 그대로 배포하기 위한 것이 아니다.

Claude Code가 현재 Next.js 앱의 기능을 유지하면서, 검토된 디자인을 React/Tailwind 구조로 옮길 수 있도록 다음을 제공한다.

## 구성

| 파일 | 역할 |
|---|---|
| `CLAUDE.md` | `harness/apps/web/`에 둘 로컬 Claude Code 지침 |
| `PROMPT_FOR_CLAUDE_CODE.md` | Claude Code에 처음 전달할 실행 프롬프트 |
| `VISUAL_CONTRACT.md` | 색상·타이포·레이아웃의 canonical 디자인 규칙 |
| `PAGE_MAPPING.md` | HTML 레퍼런스와 실제 Next.js route 매핑 |
| `COMPONENT_MAPPING.md` | 현재 컴포넌트별 변경 전략 |
| `IMPLEMENTATION_PLAN.md` | 회귀를 줄이는 Slice 순서 |
| `ACCEPTANCE.md` | 구현 완료 판단 기준 |
| `CONTRACT_CHANGE_PROPOSAL.md` | 기존 디자인 contract 변경 제안 초안 |
| `DESIGN_TOKENS.css` | 적용할 CSS variable 초안 |
| `reference/` | 최종 검토된 주황·베이지 HTML 레퍼런스 전체 |

## 레포에 넣는 위치

```text
Dreammate-Studio/
└── harness/
    └── apps/
        └── web/
            ├── CLAUDE.md
            └── design_reference/
                ├── README.md
                ├── PROMPT_FOR_CLAUDE_CODE.md
                ├── VISUAL_CONTRACT.md
                ├── PAGE_MAPPING.md
                ├── COMPONENT_MAPPING.md
                ├── IMPLEMENTATION_PLAN.md
                ├── ACCEPTANCE.md
                ├── CONTRACT_CHANGE_PROPOSAL.md
                ├── DESIGN_TOKENS.css
                └── reference/
```

## 권장 사용

1. 이 패킷을 위 경로에 복사한다.
2. Claude Code를 저장소 루트 또는 `harness/apps/web`에서 실행한다.
3. `PROMPT_FOR_CLAUDE_CODE.md`의 프롬프트를 전달한다.
4. 첫 응답에서는 구현하지 말고 repo audit와 Slice 계획만 받는다.
5. 계획을 확인한 뒤 Slice 1부터 구현시킨다.

## 중요

현재 레포는 단순 목업이 아니라 API, SSE, Auth, PKM, 피드백이 연결된 앱이다.

따라서 시각적으로 비슷하게 만드는 것보다 다음이 우선이다.

- 기존 동작 보존
- route 보존
- 부분 결과 보존
- 모바일 CTA 겹침 방지
- PlanCard 보호
- 타입·빌드 통과
