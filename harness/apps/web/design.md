# design.md

## 1. Design Purpose

영상기획 AI 에이전트의 Next.js PWA 프론트엔드 설계 기준을 정의한다.

## 2. Product UX Principle

- AI는 바로 긴 결과물을 만들지 않고 먼저 사용자의 의도를 정리한다.
- 핵심 UX는 입력 → 방향 확인 → 생성 → 검증 → 저장이다.
- 모바일에서는 한 화면에 하나의 주요 행동만 보여준다.
- 결과물은 카드 단위로 나눈다.
- 사용자는 AI 결과를 수정, 저장, 재생성할 수 있어야 한다.

## 3. Target User Context

- 개인 크리에이터
- 동아리/소규모 팀 운영자
- 초기 브랜드/소상공인

## 4. Information Architecture

```text
Landing
├── Login
├── Dashboard
│   ├── New Video Plan
│   ├── Saved Plans
│   └── Settings
```

## 5. Core User Flow

```text
사용자 입력
→ AI 의도 분석
→ 부족한 정보 질문
→ 한 줄 방향 승인
→ RAG 기반 기획 생성
→ Critic Agent 검증
→ 개선 제안
→ 저장/수정/재생성
```

## 6. Page Structure

MVP Pages:

1. Landing
2. Login
3. Dashboard
4. New Video Plan
5. Direction Approval
6. Generation Progress
7. Planning Result
8. Saved Plan Detail
9. Settings

## 7. Component System

Input:

- PromptInput
- FormatSelector
- ToneSelector
- TargetSelector
- IntentQuestionCard
- ChecklistSelector

AI Flow:

- DirectionApprovalCard
- GenerationProgressStepper
- RAGReferencePanel
- AgentStatusIndicator

Output:

- OneLineDirectionCard
- HookCandidateCard
- VideoStructureTimeline
- ShootingNoteCard
- QualityScorePanel
- RevisionSuggestionCard
- SavePlanButton

## 8. Layout Rules

- 모바일 기준 세로 스크롤을 우선한다.
- 주요 CTA는 하단 고정 버튼을 우선 사용한다.
- 결과물은 섹션별 카드로 구분한다.
- 긴 텍스트는 접기/펼치기 구조를 사용한다.

## 9. Responsive Design Rules

Mobile 기준 360px~430px 폭을 우선한다. Desktop은 좌측 사이드바 + 중앙 작업 영역 + 우측 품질 검토 패널 구조를 검토할 수 있다.

## 10. PWA & Mobile Usage Rules

- 모바일 웹에서 사용 가능한 PWA를 우선 설계한다.
- 오프라인 완전 지원과 푸시 알림은 MVP에서 제외한다.
- Expo 전환 시 API, shared types, output schema는 유지한다.

## 11. Visual Style Guide

신뢰감 있는 AI 생산성 도구, 실용적이고 정돈된 카드 기반 UI, 명확한 CTA를 지향한다.

## 12. Accessibility Rules

버튼 터치 영역, 폼 라벨, 오류 메시지, 색상 대비, 짧은 문단을 고려한다.

## 13. Motion & Interaction Rules

애니메이션은 생성 진행 상태를 이해시키는 용도로만 사용한다.

## 14. AI Interaction Rules

- 사용자의 승인 전 최종 기획안을 생성하지 않는다.
- 생성 중 현재 단계가 무엇인지 표시한다.
- 검증 결과는 점수, 이유, 개선안을 함께 제공한다.

## 15. Output Display Rules

표시 순서:

1. 한 줄 기획 방향
2. 타겟 분석
3. 후킹 후보 3개
4. 영상 구성안
5. 촬영 노트
6. 품질 평가 점수
7. 개선 제안
8. 저장/수정/재생성 버튼

## 16. State & Error Rules

필수 상태:

- Empty
- Loading
- Streaming
- Partial Result
- Error
- Retry
- Save Success

## 17. MVP Design Scope

포함: Landing, Login, Dashboard, New Plan, Direction Approval, Generating, Result, Detail, Settings.  
제외: Billing, Team, Admin, Auto Video Editing.

## 18. Expansion Design Scope

Brand Memory, 팀 협업, 크레딧/결제, 관리자 로그, RAG 지식 관리, Expo 앱.

## 19. Design Review Checklist

- [ ] 입력 → 방향 승인 → 생성 → 검증 → 저장 흐름이 보이는가?
- [ ] 한 줄 기획 방향 승인 단계가 있는가?
- [ ] 모바일 CTA가 명확한가?
- [ ] 결과물이 카드 구조인가?
- [ ] AI 생성 상태가 단계별로 표시되는가?
- [ ] 영상 제작/편집 UI가 들어가지 않았는가?
