# agent.html - Harness Dashboard MVP Spec

> **위치**: `tools/agent_html_spec.md` (하네스 안에 보관)
> **버전**: v1.0.0
> **상태**: 설계 명세 (구현 대기)
> **구현 주체**: Claude Code (1차 빌드) → Codex / Copilot Code 교대 유지보수

---

## 1. 목적과 비목적

### 목적

영상 기획 에이전트 프로젝트의 하네스(`PROJECT_STATE`, Phases, Proposals, Decisions, Skills, Contracts)를 시각적으로 관리하고 일부 액션(승인/거절/상태 전환)을 UI로 처리한다. 토큰 최적화 압축 레이어 역할 동시 수행.

### 비목적

- ❌ Claude 인터페이스 대체
- ❌ 영상 기획 에이전트 본체의 일부
- ❌ 외부 공유용 (localhost only)
- ❌ Contract 본문 직접 편집 (contract-change Skill 우회 금지)
- ❌ Skill 본문 직접 편집 (마찬가지)
- ❌ 영상 생성/편집

### 핵심 원칙

```
1. HTML은 보조, Claude는 본체.
2. HTML은 "결정과 상태", Claude는 "내용과 분석".
3. 모든 contract 변경은 여전히 contract-change Skill 절차를 거친다.
4. HTML은 토큰을 줄이는 압축 레이어다.
```

---

## 2. 5개 화면 (MVP 범위)

### Screen 1. Dashboard

#### 목적
열었을 때 "지금 봐야 할 것"이 30초 안에 파악되는 한 화면.

#### 표시

```
[상단 상태바]
- 현재 Phase: 04-mvp-frontend-discovery (60% 진행 중)
- 마지막 Phase 종료: 03-mvp-auth (2026-01-10)
- 마지막 contract-change: 2026-01-12

[알람 영역]
- 🔴 미해결 Critical: 0
- 🟡 미해결 High: 2
- 🔵 미해결 Medium: 5
- ⚪ Pending Proposals: 3

[Quick Actions]
- [현재 Phase 진행 보기]
- [미결 Proposal 처리]
- [최근 결정 보기]
- [세션 시드 복사] ← 토큰 최적화의 핵심

[최근 활동 타임라인]
2026-01-13 14:30  proposal P-2025-01-13 등록
2026-01-13 12:15  Phase 04 acceptance 2/5 통과
2026-01-12 18:00  prompt P-006 v1.1.0 활성화
...
```

#### 액션

```
✅ 클릭 한 번으로 가능
- Phase 화면으로 이동
- Proposal 화면으로 이동 (필터 적용)
- Decision 화면으로 이동
- 세션 시드 JSON을 클립보드에 복사

❌ 여기서 직접 안 함
- Phase 상태 변경 (Phases 화면에서)
- Proposal 승인 (Proposals 화면에서)
```

#### 데이터 의존

```
Read:
  PROJECT_STATE.md (current_phase, last_phase_done)
  PHASE_REGISTRY.md (현재 Phase의 progress)
  meta/proposals/*.md (status === 'pending')
  docs/bug_reports/*.md (status !== 'closed')
  agent_io_logs (recent 10건, last 24h)

Compute:
  알람 카운트 (severity별)
  Phase 진행률 (acceptance.md의 [x]/[ ] 비율)
  Quick Actions 가능 여부
```

#### 세션 시드 (토큰 최적화 핵심)

`session_seed.json` 1KB 이내로 압축. Claude 세션 시작 시 사용자가 복사 → Claude에 붙여넣기:

```json
{
  "as_of": "2026-01-13T14:30:00Z",
  "current_phase": {
    "id": "04-mvp-frontend-discovery",
    "progress": 0.6,
    "open_items": 3
  },
  "alerts": { "critical": 0, "high": 2, "medium": 5 },
  "pending_proposals": 3,
  "recent_decisions": [
    "P-006 v1.1.0 활성화",
    "design.md 색상 변경 승인"
  ],
  "last_session_handoff": "meta/handoffs/2026-01-12-1800.md"
}
```

이걸 Claude에 주면 Claude가 PROJECT_STATE / PHASE_REGISTRY / proposals 폴더를 일일이 안 읽어도 됨. 약 5K–10K 토큰 절약.

---

### Screen 2. Phases

#### 목적
Phase 전체 트리 + 각 Phase 진행 상태 한눈에.

#### 표시

```
[필터 탭]
[ All ] [ Active ] [ Done ] [ Pending ] [ Abandoned ]

[Phase 카드 (status별 색 구분)]
┌─────────────────────────────────────┐
│ 🟢 04-mvp-frontend-discovery (active) │
│ ─────────────────────────────────── │
│ 시작: 2026-01-10                     │
│ 진행: ████████░░ 60% (3/5)           │
│ 의존: 03-mvp-auth ✅                 │
│ 다음: 05-mvp-quick-mode              │
│ Acceptance:                          │
│   [x] Discovery 5단계 카드           │
│   [x] choice_logs 저장               │
│   [x] 모바일 360px 통과              │
│   [ ] 광고 표현 검출 로직            │
│   [ ] Intent Filter UX               │
│ [Phase 폴더 열기] [회고 보기]        │
└─────────────────────────────────────┘
```

#### 액션

```
✅ HTML에서 직접 가능
- Phase status 전환 (pending → active, active → done)
  → PHASE_REGISTRY.md 갱신만 (claude 호출 없이)
  → 단, active → done 전환 시 phase-complete Skill 안내 표시
- Phase 폴더 파일 트리 열기 (read-only)
- Acceptance 체크박스 토글 (acceptance.md 직접 갱신)

⚠️ Claude를 통해서만 가능 (HTML에선 안내만)
- 새 Phase 생성 (phase-start Skill 트리거 필요)
- Phase 폐기 (closing_notes 작성 필요)
- contract 변경이 따르는 작업
```

#### 데이터 의존

```
Read:
  PHASE_REGISTRY.md
  phases/active/*/acceptance.md (체크박스 파싱)
  phases/active/*/goals.md (요약 표시)
  phases/archive/**/*.md (done phases)
  phases/abandoned/**/*.md

Write:
  PHASE_REGISTRY.md (status 전환)
  phases/active/*/acceptance.md (체크박스 갱신)
  PROJECT_STATE.md (current_phase 자동 갱신)
```

---

### Screen 3. Proposals

#### 목적
모든 contract-change 제안을 한 곳에서 처리.

#### 표시

```
[필터]
status: [ Pending ] [ Approved ] [ Rejected ] [ All ]
target:  [ All Contracts ▼ ]  search: [______]

[Proposal 목록 (pending 우선)]
┌──────────────────────────────────────────┐
│ 🟡 P-2026-01-13-fix-schema-output         │
│ ─────────────────────────────────────── │
│ 대상: docs/contracts/output_schema.md     │
│ 종류: breaking change                    │
│ 등록: 2026-01-13 (claude)                │
│ 영향: API, Agent IO, Frontend            │
│ Rollback: 가능 (v1.0 fallback path 명시) │
│                                          │
│ 사유 요약: Critic 결과에 confidence 필드  │
│ 추가하여 Rewriter 분기 정밀도 향상.       │
│                                          │
│ [본문 펼치기] [승인] [거절] [수정 요청]  │
└──────────────────────────────────────────┘
```

#### 액션

```
✅ HTML에서 직접 가능
- Proposal 본문 열기 (read-only)
- 승인 클릭 → proposal status: 'approved'
- 거절 클릭 → status: 'rejected' + 이유 입력
- 수정 요청 → status: 'needs_revision' + 코멘트

⚠️ 승인 후 자동 처리 안 됨
- HTML은 proposal status만 갱신
- 실제 contract 파일 변경은 Claude가 contract-change Skill로 진행
- 사용자가 다음 Claude 세션에서 "P-2026-01-13 승인됐어, 반영해줘"

이유: contract 본문 편집은 깊은 영향 분석 필요 → Claude 책임 유지
```

#### 데이터 의존

```
Read:
  meta/proposals/*.md (frontmatter + 본문)

Write:
  meta/proposals/*.md (status, 결정자, 결정일, 메모 필드만)
```

#### 토큰 최적화 효과

```
Claude가 proposal 검토 시 raw 본문 (평균 500–1500 토큰) 안 읽어도 됨.
HTML이 사용자에게 본문 보여주고, 사용자가 승인하면 Claude에는
"P-XXX 승인됨, 반영해줘"만 (50 토큰).

세션당 절약: 1,000–4,000 토큰 (proposal 3–5개 처리 기준)
```

---

### Screen 4. Decisions

#### 목적
모든 ADR(Architecture Decision Records)을 검색 가능한 형태로.

#### 표시

```
[검색바]    [______________________]
[태그 필터] [ phase: all ▼ ] [ area: all ▼ ] [ date: all ▼ ]

[Decision 카드 목록]
┌──────────────────────────────────────────┐
│ D-2025-12-15 Discovery + Quick 하이브리드 │
│ ─────────────────────────────────────── │
│ Phase: 01-design                          │
│ Area: UX                                  │
│ 결정자: aiden                             │
│ 1줄 요약: 신규는 Discovery, 기존 Series  │
│ 추가는 Quick으로 분기                    │
│ [본문 보기]                              │
└──────────────────────────────────────────┘
```

#### 액션

```
✅ HTML에서 가능
- 검색 (제목 + 본문 풀텍스트)
- 태그 필터 (phase, area, date)
- 본문 열기 (read-only)
- 태그 추가/수정 (frontmatter 갱신만)

⚠️ Claude를 통해서만
- 새 Decision 작성 (분석 필요)
- Decision 본문 수정 (의미 변경 시 contract-change 절차)
```

#### 데이터 의존

```
Read:
  docs/decisions/*.md (frontmatter + 본문 + 태그)

Write:
  docs/decisions/*.md (태그만, 본문은 read-only)

Index:
  fuse.js 또는 lunr.js로 클라이언트 사이드 풀텍스트 인덱스
```

#### 토큰 최적화 효과

```
"Phase 4에서 어떤 결정 있었지?" 같은 질문을 Claude에 안 함.
HTML에서 phase 태그 필터 → 즉시 확인.

세션당 절약: 2,000–8,000 토큰 (자주 일어나는 패턴)
```

---

### Screen 5. Search

#### 목적
하네스 전체 markdown 파일을 풀텍스트 검색.

#### 표시

```
[검색바]   [______________________]
[범위]    □ Contracts  □ Decisions  □ Proposals  □ Phases
          □ Skills    □ Eval Reports □ Handoffs

[결과 (관련도 순)]
┌──────────────────────────────────────────┐
│ docs/contracts/db_schema.md              │
│ ─────────────────────────────────────── │
│ "candidate_knowledge 테이블의 status 컬럼은 │
│ pending, filtered, evaluated, approved,   │
│ promoted, rejected 중 하나..."           │
│                                          │
│ Phase: 02-design  |  Area: DB            │
│ [열기]                                   │
└──────────────────────────────────────────┘
```

#### 액션

```
✅ HTML에서 가능
- 풀텍스트 검색
- 결과 클릭 → 해당 파일 열기 (read-only)
- 검색 결과를 Claude에 전송 (클립보드)

❌ 여기서 안 함
- 검색 결과 수정
- 파일 삭제
```

#### 데이터 의존

```
Read:
  하네스 전체 *.md 파일
  
Index:
  로컬 서버 시작 시 인덱싱 (변경 감지 watch)
  fuse.js 또는 lunr.js
  
캐싱:
  변경 없는 파일은 디스크 캐시 (인덱스 재빌드 빠르게)
```

#### 토큰 최적화 효과

```
"하네스에서 RAG 관련 내용 어디 있어?" 같은 질문 Claude에 안 함.
HTML 검색 → 클릭 → 필요한 부분만 Claude에 전달.

세션당 절약: 3,000–10,000 토큰 (사용 빈도 높음)
```

---

## 3. 토큰 최적화 데이터 계약

### 3-1. 4-Layer Compression

```
Layer 1: Raw harness files (디스크)
   ↓ (HTML 서버가 watch하며 자동 변환)
Layer 2: JSON manifests (메모리 또는 .cache/)
   ↓ (Dashboard 로드 시 추출)
Layer 3: session_seed.json (~500–1,500 토큰)
   ↓ (사용자 복사 → Claude 세션 시작 시 붙여넣기)
Claude context
```

### 3-2. JSON Manifest 구조

#### `state.json` (전체 상태 요약)

```json
{
  "as_of": "ISO-8601",
  "current_phase": {
    "id": "string",
    "status": "active|pending|done|abandoned",
    "progress": "float (0–1)",
    "open_items": "int",
    "started_at": "ISO-8601",
    "blockers": ["string"]
  },
  "alerts": {
    "critical": "int",
    "high": "int",
    "medium": "int",
    "low": "int"
  },
  "pending_proposals": "int",
  "open_bugs": "int",
  "last_eval_result": "pass|fail|null",
  "last_cost_snapshot": {
    "weekly_usd": "float",
    "wow_change": "float"
  }
}
```

크기: ~300 토큰.

#### `phases.json`

```json
{
  "phases": [
    {
      "id": "04-mvp-frontend-discovery",
      "status": "active",
      "progress": 0.6,
      "acceptance": { "total": 5, "passed": 3 },
      "dependencies": ["03-mvp-auth"],
      "dependencies_met": true,
      "next_phase": "05-mvp-quick-mode",
      "started_at": "2026-01-10",
      "completed_at": null
    }
  ]
}
```

크기: ~50 토큰/phase. 22 phase 가정 시 약 1.1K 토큰.

#### `proposals.json`

```json
{
  "pending": [
    {
      "id": "P-2026-01-13-fix-schema",
      "target": "docs/contracts/output_schema.md",
      "kind": "breaking",
      "submitted_at": "2026-01-13T14:00:00Z",
      "summary_one_line": "Critic 결과에 confidence 필드 추가",
      "affected_areas": ["api", "agent_io", "frontend"],
      "rollback_possible": true
    }
  ]
}
```

크기: ~80 토큰/proposal.

#### `decisions_index.json`

전체 ADR의 인덱스만. 본문은 안 포함:

```json
{
  "decisions": [
    {
      "id": "D-2025-12-15",
      "title": "Discovery + Quick 하이브리드",
      "phase": "01-design",
      "area": "ux",
      "tags": ["mode", "user-flow"],
      "summary_one_line": "신규 사용자는 Discovery, 기존 Series 추가는 Quick",
      "file_path": "docs/decisions/2025-12-15-hybrid-ux.md"
    }
  ]
}
```

크기: ~60 토큰/decision.

### 3-3. Session Seed (가장 중요)

Claude 세션 시작 시 사용자가 복사해 붙여넣는 압축 시드:

```json
{
  "as_of": "2026-01-13T14:30:00Z",
  "phase": "04-mvp-frontend-discovery (60%, 2/5 open)",
  "alerts": "0C/2H/5M",
  "pending_proposals": 3,
  "recent_decisions": [
    "D-2026-01-12 prompt P-006 v1.1.0 활성화",
    "D-2026-01-10 design.md 강조색 #3B5BDB"
  ],
  "last_handoff": "meta/handoffs/2026-01-12-1800.md",
  "next_first_task": "광고 표현 검출 로직 구현 (acceptance #4)"
}
```

**크기: ~250–500 토큰**.

이 시드만 Claude에 주면 "지금 어디 있고 뭐 할 차례인지" 다 들어감. PROJECT_STATE + PHASE_REGISTRY + 최근 proposals 따로 안 읽어도 됨.

**기대 절약: 세션 시작당 5K–10K 토큰**.

---

## 4. 기술 스택

```
Frontend: Next.js 14 (App Router) + TypeScript
Styling:  Tailwind CSS + shadcn/ui (영상 에이전트 본체와 동일 스택, 학습 비용 0)
Backend:  Next.js API Routes (별도 서버 안 둠) 또는 FastAPI (Python 친화 시)
Storage:  로컬 파일시스템 직접 read/write (DB 없음)
Search:   fuse.js (클라이언트) + chokidar (서버 watch)
포트:     localhost:7777 (충돌 없는 임의 포트)
인증:     없음 (localhost only, 외부 노출 금지)
```

### 의존성 최소화

```
package.json (예상):
  next, react, react-dom, typescript, tailwindcss
  fuse.js, gray-matter (frontmatter 파싱)
  chokidar (파일 변경 감지)
  lucide-react (아이콘)
  
총: ~10개 라이브러리
```

---

## 5. Claude Code 빌드 브리프

다음 세션에서 Claude Code에 이 spec과 함께 전달할 빌드 지시.

### 5-1. 프로젝트 생성

```
1. 디렉터리: tools/agent-html/
2. Next.js 14 App Router로 초기화
3. Tailwind + shadcn/ui 설정
4. 디렉터리 구조:
   tools/agent-html/
   ├── app/
   │   ├── page.tsx              # Dashboard
   │   ├── phases/page.tsx
   │   ├── proposals/page.tsx
   │   ├── decisions/page.tsx
   │   └── search/page.tsx
   ├── lib/
   │   ├── harness-reader.ts     # 하네스 파일 read
   │   ├── harness-writer.ts     # 제한된 write (status 필드만)
   │   ├── manifests.ts          # JSON manifest 생성
   │   └── session-seed.ts       # 세션 시드 생성
   ├── api/
   │   ├── state/route.ts
   │   ├── phases/[id]/route.ts
   │   ├── proposals/[id]/route.ts
   │   ├── decisions/route.ts
   │   └── search/route.ts
   └── components/ui/            # shadcn/ui
```

### 5-2. 안전 가드

```
HARNESS_ROOT 환경 변수 (기본: ../../)
화이트리스트 경로만 write 허용:
  - PROJECT_STATE.md (current_phase, last_phase_done 필드만)
  - PHASE_REGISTRY.md (status 필드만)
  - phases/*/acceptance.md (체크박스만)
  - meta/proposals/*.md (status, 결정 메타만)
  - docs/decisions/*.md (frontmatter 태그만)

화이트리스트 외 경로 write 시도 → 거절 + 로그
contract 파일 본문 write → 항상 거절 (Claude를 통하라는 안내 표시)
```

### 5-3. 토큰 최적화 점검 항목

```
[ ] state.json이 500 토큰 이하인가?
[ ] phases.json이 phase당 50 토큰 이하인가?
[ ] proposals.json이 proposal당 80 토큰 이하인가?
[ ] decisions_index.json이 decision당 60 토큰 이하인가?
[ ] session_seed.json이 500 토큰 이하인가?
[ ] 같은 파일 두 번 읽지 않는가? (캐싱)
[ ] Markdown 본문은 사용자 클릭 시에만 로드되는가?
[ ] 검색은 클라이언트 사이드에서 처리되는가?
```

### 5-4. 작동 검증 시나리오

Claude Code가 빌드 완료 후 다음 시나리오 모두 통과:

```
1. localhost:7777 접속 → Dashboard 로드 (1초 이내)
2. Dashboard에서 "세션 시드 복사" 클릭 → 클립보드에 JSON
3. Phases 탭 → 모든 Phase 카드 표시 (active 강조)
4. 한 Phase의 acceptance 체크박스 토글 → acceptance.md 갱신 확인
5. Proposals 탭 → pending 목록 표시
6. proposal 승인 → meta/proposals/*.md의 status 필드 갱신
7. Decisions 탭 → 검색바에 단어 입력 → 결과 즉시 필터링
8. Search 탭 → 전체 markdown 검색 → 관련도 순 결과
9. contract 파일 직접 write 시도 → 거절 메시지
10. 외부 IP에서 접근 시도 → 거절 (localhost only)
```

---

## 6. 다중 모델 유지보수 워크플로

### 6-1. 1차 빌드

```
세션 1 (Claude Code):
- 이 spec 첨부
- MVP 5 화면 전체 구현
- 작동 검증 시나리오 통과
- 산출물: tools/agent-html/ 폴더 전체
```

### 6-2. 업데이트 사이클

```
교대 순서 (회전):
  Round 1: Claude Code
  Round 2: Codex (GPT-5 기반)
  Round 3: Copilot Code (Claude 계열)
  Round 4: Claude Code (다시 시작)

업데이트 유형:
  - 버그 수정 → 발견자 모델이 진행
  - 새 기능 → 라운드 순서대로
  - 리팩토링 → 라운드 순서대로
```

### 6-3. 모델 간 일관성 보장

각 모델에 전달할 표준 컨텍스트 패키지:

```
필수 첨부:
1. tools/agent_html_spec.md (이 문서)
2. tools/agent-html/CLAUDE.md (변경 이력 + 다음 모델에게 인계)
3. 현재 변경 대상 파일

CLAUDE.md 템플릿:
  ## 변경 이력
  - 2026-01-XX (Claude Code): MVP 5 화면 빌드
  - 2026-01-XX (Codex): Dashboard 알람 임계값 조정
  - 2026-01-XX (Copilot): Search 인덱스 캐싱 추가
  
  ## 현재 상태
  - 작동 정상
  - 알려진 이슈: ...
  - 다음 작업: ...
  
  ## 다음 모델에게
  - {특정 인계 사항}
```

### 6-4. 모델 간 차이 흡수

```
Claude Code 특성: 문서/명세 잘 따름. 안전 가드 잘 지킴.
Codex 특성:       빠른 코드 작성. 안전 검증 약함. 추가 검토 필요.
Copilot 특성:     Claude 기반. 보수적. 큰 변경에 신중.

→ 위험도 매트릭스:
  버그 수정: 어떤 모델이든 OK
  새 기능:   Claude Code 또는 Copilot 우선
  리팩토링:  Claude Code 우선 (안전 가드 영향)
  성능 최적화: Codex 우선 (빠른 반복)
```

### 6-5. multi-llm-validation Skill 활용

큰 변경(아키텍처 변경, 새 화면 추가)은 3개 모델 모두 검토 후 결정:

```
1. 변경 제안 → 3개 모델에게 같은 컨텍스트 전달
2. 각 모델 응답 비교 → 합의 / 불일치 분석
3. 합의 사항만 채택
4. 채택된 변경을 라운드 순서 다음 모델이 구현
```

---

## 7. Phase 등록 (하네스 안에서)

이 작업을 정식 Phase로 PHASE_REGISTRY.md에 등록:

```yaml
phase: tools-agent-html-mvp
status: pending
dependencies:
  - 00-harness-stabilization  # 안정화 끝나야 진입
priority: medium
estimated_sessions: 2
estimated_dev_hours: 28
description: |
  하네스 관리 + 토큰 최적화 보조 도구.
  영상 에이전트 본체와 독립 운영.
acceptance:
  - 5 화면 작동 검증 시나리오 통과
  - session_seed.json 500 토큰 이하 달성
  - 안전 가드 (화이트리스트 외 write 거절) 통과
  - localhost only 강제
non_goals:
  - 외부 노출
  - Contract 본문 편집
  - 영상 생성/편집
```

---

## 8. 확장 (MVP 이후)

MVP 5 화면 운영 안정화 후 추가 후보 (이 spec의 범위 밖):

```
- Cost Dashboard      (agent_io_logs 시각화)
- Skill Usage Stats   (meta/skill_usage_log.md 시각화)
- Eval History        (regression_results 추이 그래프)
- Quick Actions       (새 Phase 생성, Skill 시뮬레이션)
- Multi-LLM 패널      (3개 모델 응답 동시 보기)
```

각 확장은 별도 Phase로 등록.

---

## 9. 종료 / 폐기 기준

agent.html을 폐기할 경우 (있다면):

```
- 토큰 절약 효과가 운영 1개월 후 측정해 5K/세션 미만이면 폐기 후보
- 유지보수 부담이 효과를 초과하면 폐기
- Claude.ai에 동등 기능이 네이티브 추가되면 마이그레이션
```

폐기 시:
- 모든 manifest 파일 삭제
- tools/agent-html/ 디렉터리 제거
- 이 spec은 보관 (재구축 시 참조)

---

## 10. Open Questions

이 spec 확정 전 답해야 할 것:

1. HARNESS_ROOT를 어디로 설정할지 (실제 하네스 폴더 경로)
2. session_seed.json을 자동으로 클립보드에 복사할지, 다운로드할지
3. proposal 승인 시 Claude 세션에 자동 알림 보낼 수단이 있는지 (또는 사용자 수동)
4. 검색 인덱스 크기가 크면 (파일 1000개 이상) lazy 인덱싱 필요한가
5. 다국어 지원 (한국어 + 영어 검색) 우선순위

답은 다음 세션에서 (또는 Claude Code 빌드 중에) 결정.

---

## 참조

- 본 명세는 다음 하네스 산출물에 의존:
  - `apps/web/design.md` (스타일 가이드)
  - `docs/contracts/db_schema.md` (메타데이터 구조)
  - `.skills/INDEX.md` (Skill 라우팅)
  - `.skills/contract-change/SKILL.md` (write 제한 정책 근거)
  - `.skills/context-compact/SKILL.md` (세션 시드 개념의 기반)

- 변경 절차: 이 spec 자체도 contract-change Skill로 변경한다.
- 변경 이력은 `meta/proposals/`에 기록.
