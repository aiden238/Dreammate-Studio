# Dreammate Studio — 영상기획 AI 에이전트 플랫폼

> 사용자의 목적·타겟·브랜드 톤을 정리하고, LLM Wiki와 RAG로 근거를 찾은 뒤,  
> 검증 에이전트가 기획 품질을 평가·개선하는 **영상기획 특화 AI 에이전트**.

영상 제작 AI가 아니라 **영상기획 AI 에이전트**입니다.

---

## 현재 상태

| 항목 | 내용 |
|---|---|
| **Phase** | Phase 1 — MVP 기본 플로우 (active) |
| **이전 Phase** | Phase 0 — 하네스 마이그레이션 ✅ done (2026-05-26) |
| **하네스 규모** | 200+ 파일, ~50,000줄 |
| **Skill 구조** | `.claude/skills/` 단일 (20개, applies_to 태그) |
| **Repository** | https://github.com/aiden238/Dreammate-Studio (Private) |

---

## 핵심 흐름

```text
사용자 입력
→ 의도 분석 (Discovery Wizard 또는 Quick Mode 자동 분기)
→ 부족한 정보 질문 (Discovery: 5 카드, Quick: 1–2 질문)
→ 한 줄 기획 방향 승인
→ LLM Wiki / RAG Lite 검색
→ 영상기획안 생성 (Phase 1: 1개, Phase 4+: 3개)
→ Critic Agent 검증 (revise 최대 2회)
→ 결과 저장
→ 사용자 피드백 저장 (Brand Memory 자동 추출)
```

**UX 분기 조건:**  
- 신규 / Brand 없음 → **Discovery Wizard** (5단계 카드)  
- 기존 Series → **Quick Mode** (1–2 질문만)

---

## 폴더 구조

```
Dreammate_Studio/
├── README.md                  ← 이 파일
├── .gitignore
├── harness/                   ← 하네스 (운영 중)
│   ├── 00_START_HERE.md       ← 첫 진입 시 여기부터
│   ├── CLAUDE.md              ← 기획/설계 모델 라우터
│   ├── AGENTS.md              ← 구현/QA 모델 라우터
│   ├── PROJECT_STATE.md       ← 현재 작업 상태
│   ├── PHASE_REGISTRY.md      ← Phase 목록 (0~30)
│   ├── .claude/skills/        ← Skill 20개 (단일 폴더, applies_to 태그)
│   ├── ai_system/             ← MOA Lite + RAG Lite 구조
│   ├── apps/web/              ← Next.js PWA 설계
│   ├── backend/               ← FastAPI + Spring (placeholder)
│   ├── docs/contracts/        ← 모든 결정의 단일 진실 소스
│   ├── eval/                  ← 평가 체계 + golden_set
│   ├── knowledge/             ← LLM Wiki + RAG 지식
│   ├── meta/                  ← 운영 가이드 + 회고
│   ├── phases/active/         ← 현재 Phase 문서
│   ├── phases/archive/        ← 완료 Phase (기본 참조 금지)
│   ├── product/               ← 비전 + 범위 + 로드맵
│   └── tests/ packages/ logs/ ← Phase 진행에 따라 채움
└── _staging/                  ← 이식 소스 (참조용, 변경 금지)
```

---

## Phase 이력

| Phase | 이름 | 상태 | 완료일 |
|---|---|---|---|
| 0 | 하네스 초기화 (Migration) | ✅ done | 2026-05-26 |
| **1** | **MVP 기본 플로우** | **🔵 active** | — |
| 2 | design.md 기반 PWA 설계 | pending | — |
| 3 | Next.js PWA 기본 UI 구현 | pending | — |
| 4 | FastAPI 기본 백엔드 구현 | planned | — |
| 5 | DB / Auth 기본 구조 | planned | — |
| 6~10 | AI System + 통합 테스트 | planned | — |
| 11~30 | 안정화 / 확장 / 고도화 | future | — |

Sprint S0~S5 (Phase 0) 모두 완료 — 6개 commit, 11/11 acceptance 통과.

---

## 기술 스택

| 계층 | MVP (Phase 1~10) | 확장 (Phase 21+) |
|---|---|---|
| Frontend | Next.js 14 PWA | Expo React Native |
| Backend | FastAPI (Python) | Spring Boot |
| DB | PostgreSQL + pgvector (Supabase) | — |
| LLM | gpt-4o-mini (기본) / gpt-4o (Critic) | Custom Fine-tune |
| RAG | pgvector + candidate_knowledge 5단계 | Custom RAG |

---

## 확정 결정 사항 (주요 25개)

1. Discovery + Quick 하이브리드 UX (1.6x 비용 수용)
2. Mode 자동 분기: 신규 → Discovery, 기존 Series → Quick
3. Discovery 단계당 카드 5장 (AI 4 + 직접입력 1)
4. Plan 후보 3개 생성 (Phase 4+, Phase 1은 1개)
5. Critic revise 최대 2회 (무한 루프 차단)
6. 4계층 데이터 모델 (Brand / Domain / Series / VideoProject)
7. Intent Filter (영상기획 외 입력 차단)
8. Brand Memory 자동 추출 + 사용자 검토 가능
9. 광고적 표현 차단 단어 검사 ("최고의", "혁신적인" 등)
10. 30–60초 대기 시 4단계 progress + 부분 결과 노출
11. Skill 20개, `.claude/skills/` 단일 폴더
12. 영상 자동 편집 / TTS / BGM / 자동 업로드 → MVP 영구 제외

전체 목록: `harness/PROJECT_STATE.md`의 `confirmed_decisions`

---

## 작업 진입

```
1. harness/00_START_HERE.md  ← 첫 진입 시 여기부터
2. harness/PROJECT_STATE.md  ← 현재 작업 위치 확인
3. harness/phases/active/phase-1-mvp-basic-flow/  ← Phase 1 컨텍스트
```

---

## 주의사항

- `docs/contracts/`는 무단 변경 금지 — `contract-change` Skill 절차 필수
- `phases/archive/`는 기본 참조 금지
- 영상 제작 기능은 MVP에 넣지 않는다 (mvp_non_goals.md 참조)
- contract와 다른 문서가 충돌 시 → contract 우선
